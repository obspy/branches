#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ObsPySOD: ObsPy Standing Order for Data tool. Meant to be used from the shell.
This has been part of a Bachelor's Thesis at the University of Munich.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""

import sys
import os
import time
import pickle
# do not need signal, no ^c handling - quit d/l with q now.
# left the remainders in the code since it would be nicer to have 1 thread
# and real ^c handling - perhaps someone will pick up on this, had to give up
#import signal
from ConfigParser import ConfigParser
from optparse import OptionParser
from obspy.core import UTCDateTime, read
import obspy.neries
import obspy.arclink
import obspy.iris
from obspy.mseed.libmseed import LibMSEED
from lxml import etree
from obspy.taup import taup
# using these modules to wrap to custom(long) help function
from textwrap import wrap
from itertools import izip_longest
# using threads to be able to capture keypress event without a GUI like
# tkinter or pyqt and run the main loop at the same time.
# This should run cross-platform...
import threading
import termios
TERMIOS = termios
# need a lock for the global quit variable which is used in two threads
lock = threading.RLock()


class keypress_thread (threading.Thread):
    """
    This class will run as a second thread to capture keypress events
    """
    global quit, done

    def run(self):
        global quit, done
        msg = 'Keypress capture thread initialized...\n'
        msg += "Press 'q' at any time to finish downloading and saving the " \
        + "last file and then quit."
        print msg
        while not done:
            c = getkey()
            print c
            if c == 'q' and not done:
                with lock:
                    quit = True
                print "You pressed q."
                msg = "Obspysod will finish downloading and saving the last " \
                + "file and quit gracefully."
                print msg
                # exit this thread
                sys.exit(0)


def getkey():
    """
    Uses termios to wait for a keypress event and return the char.
    """
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
    new[6][TERMIOS.VMIN] = 1
    new[6][TERMIOS.VTIME] = 0
    termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
    c = None
    try:
            c = os.read(fd, 1)
    finally:
            termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
    return c


def check_quit():
    """
    Checks if the user pressed q to quit downloading meanwhile.
    """
    global quit
    with lock:
        if quit:
            msg = "Quitting. To resume the download, just run " + \
            "obspysod again, using the same arguments."
            print msg
            sys.exit(0)


def main():
    """
    Main function to run as a dedicated program.
    """
    global datapath, quit, done
    # dead networks
    skip_networks = ['AI', 'BA']
    # create ConfigParser object.
    # set variable names as dict keys, default values as _STRINGS_!
    # you don't need to provide every possible option here, just the ones with
    # default values
    # need to provide default start and end time, otherwise
    # obspy.arclink.getInventory will raise an error if the user does not
    # provide start and end time
    # default for start is three months ago, end is now
    # default offset is 10 min
    config = ConfigParser({'magmin': '3',
                           'dt': '10',
                           'start': str(UTCDateTime.utcnow()
                                        - 60 * 60 * 24 * 30 * 3),
                           'end': str(UTCDateTime.utcnow()),
                           'preset': '0',
                           'offset': '600',
                           'datapath': 'obspysod-data',
                           'nw': '*',
                           'st': '*',
                           'lo': '*',
                           'ch': '*',
                          })

    # read config file, if it exists, possibly overriding defaults as set above
    config.read('.obspysodrc')

    # create command line option parser
    # parser = OptionParser("%prog [options]" + __doc__.rstrip())
    parser = OptionParser("%prog [options]")

    # configure command line options
    # action=".." tells OptionsParser what to save:
    # store_true saves bool TRUE,
    # store_false saves bool FALSE, store saves string; into the variable
    # given with dest="var"
    # * you need to provide every possible option here.
    # reihenfolge wird eingehalten in help msg.
    parser.add_option("-H", "--more-help", action="store_true",
                      dest="showhelp", help="Show explanatory help and exit.")
    helpmsg = "Instead of downloading seismic data, download metadata: " + \
              "resp instrument and dataless seed files."
    parser.add_option("-q", "--query-metadata", action="store_true",
                      dest="metadata", help=helpmsg)
    helpmsg = "The path where obspysod will store the data (default is " + \
              "./obspysod-data for the data download mode and " + \
              "./obspysod-metadata for metadata download mode)."
    parser.add_option("-P", "--datapath", action="store", dest="datapath",
                      help=helpmsg)
    helpmsg = "Update the event database when obspysod runs on the same " + \
              "directory a second time in order to continue data downloading."
    parser.add_option("-u", "--update", help=helpmsg,
                      action="store_true", dest="update")
    helpmsg = "If the datapath is found, do not resume previous downloads " + \
              "as is the default behaviour, but redownload everything. " + \
              "Same as deleting the datapath before running obspysod."
    parser.add_option("-R", "--reset", action="store_true",
                      dest="reset", help=helpmsg)
    parser.add_option("-s", "--starttime", action="store", dest="start",
                      help="Start time. Default: 3 months ago.")
    parser.add_option("-e", "--endtime", action="store", dest="end",
                      help="End time. Default: now.")
    parser.add_option("-t", "--time", action="store", dest="time",
                      help="Start and End Time delimited by a slash.")
    helpmsg = "Time parameter which determines how close the event data " + \
            "will be cropped before the event. Default: 0"
    parser.add_option("-p", "--preset", action="store", dest="preset",
                      help=helpmsg)
    helpmsg = "Time parameter which determines how close the event data " + \
            "will be cropped after the event."
    parser.add_option("-o", "--offset", action="store", dest="offset",
                      help=helpmsg)
    parser.add_option("-m", "--magmin", action="store", dest="magmin",
                      help="Minimum magnitude. Default: 3")
    parser.add_option("-M", "--magmax", action="store", dest="magmax",
                      help="Maximum magnitude.")
    helpmsg = "Provide rectangle with GMT syntax: <west>/<east>/<south>/" \
            + "<north> (alternative to -x -X -y -Y)."
    parser.add_option("-r", "--rect", action="store", dest="rect",
                      help=helpmsg)
    parser.add_option("-x", "--latmin", action="store", dest="south",
                      help="Minimum latitude.")
    parser.add_option("-X", "--latmax", action="store", dest="north",
                      help="Maximum latitude.")
    parser.add_option("-y", "--lonmin", action="store", dest="west",
                      help="Minimum longitude.")
    parser.add_option("-Y", "--lonmax", action="store", dest="east",
                      help="Maximum longitude.")
    helpmsg = "Identity code restriction, syntax: nw.st.l.ch (alternative " + \
              "to -N -S -L -C)."
    parser.add_option("-i", "--identity", action="store", dest="identity",
                      help=helpmsg)
    parser.add_option("-N", "--network", action="store", dest="nw",
                      help="Network restriction.")
    parser.add_option("-S", "--station", action="store", dest="st",
                      help="Station restriction.")
    parser.add_option("-L", "--location", action="store", dest="lo",
                      help="Location restriction.")
    parser.add_option("-C", "--channel", action="store", dest="ch",
                      help="Channel restriction.")
    helpmsg = "Do not request all networks (default), but only permanent ones."
    parser.add_option("-n", "--no-temporary", action="store_true",
                      dest="permanent", help=helpmsg)
    parser.add_option("-f", "--force", action="store_true", dest="force",
                      help="Skip working directory warning.")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Show debugging information.")

    # read from ConfigParser object's defaults section into a dictionary
    # config.defaults() (ConfigParser method) returns a dict of the default
    # options as specified above
    config_options = config.defaults()

    # config_options is dictionary of _strings_(see above dict),
    # over-ride respective correct
    # default types here with .getboolean, .getfloat, .getint
    # * you dont need to provide every possible option here, just the ones with
    # default values for which the type needs to be overriden
    config_options['magmin'] = config.getfloat('DEFAULT', 'magmin')
    config_options['dt'] = config.getfloat('DEFAULT', 'dt')
    config_options['preset'] = config.getfloat('DEFAULT', 'preset')
    config_options['offset'] = config.getfloat('DEFAULT', 'offset')
    # it's not possible to override the start and end time defaults here, since
    # they are of obspy's own UTCDateTime type. will handle below.

    # feed config_options dictionary of defaults into parser object
    parser.set_defaults(**config_options)

    # parse command line options
    (options, args) = parser.parse_args()
    if options.debug:
        print "(options, args) created"
        print "options: ", options
        print "args: ", args
    # command line options can now be accessed via options.varname.
    # check flags just like if options.flag:, so without == True, because even
    # if they do not have a default False value, they are None/don't exist,
    # which also leads to False in the if-statement

    # * override respective correct default types for _every_ possible option
    # that is not of type 'string' here. take care that it is only done if the
    # var. really exists
    if options.south:
        options.south = float(options.south)
    if options.north:
        options.north = float(options.north)
    if options.west:
        options.west = float(options.west)
    if options.east:
        options.east = float(options.east)
    # print long help if -H
    if options.showhelp:
        help()
        sys.exit()
    ## Parsing different custom command line options
    ## if the user has given e.g. -r x/x/x/x or -t time1/time
    # extract min. and max. longitude and latitude if the user has given the
    # coordinates with -r (GMT syntax)
    if options.rect:
        if options.west or options.east or options.south or options.north:
            msg = "Either provide the rectangle with GMT syntax, or with " + \
            "-x -X -y -Y, not both."
            print msg
            sys.exit(2)
        try:
            options.rect = options.rect.split('/')
            if options.debug:
                print options.rect
            if len(options.rect) != 4:
                print "Erroneous rectangle given."
                help()
                sys.exit(2)
            options.west = float(options.rect[0])
            options.east = float(options.rect[1])
            options.south = float(options.rect[2])
            options.north = float(options.rect[3])
        except:
            print "Erroneous rectangle given."
            print optarg, rect
            help()
            sys.exit(2)
        if options.debug:
            print options
    # Extract start and end time if the user has given the timeframe with
    # -t start/end (GMT syntax)
    if options.time:
        msg = "It makes no sense to provide start and end time with -s -e " + \
        "and -t at the same time, but if you do so, -t will override -s -e."
        print msg
        try:
            options.start = options.time.split('/')[0]
            options.end = options.time.split('/')[1]
        except:
            print "Erroneous timeframe given."
            help()
            sys.exit(2)
        if options.debug:
            print "options.time", options.time
            print "options.start", options.start
            print "options.end", options.end
    # Extract network, station, location, channel if the user has given an
    # identity code (-i xx.xx.xx.xx)
    if options.identity:
        msg = "It makes no sense to provide station restrictions with -i and" \
        + " -N -S -L -C at the same time, but if you do so, -i will override."
        print msg
        try:
            options.nw, options.st, options.lo, options.ch = \
                                    options.identity.split('.')
        except:
            print "Erroneous identity code given."
            help()
            sys.exit(2)
        if options.debug:
            print "options.nw:\t", options.nw
            print "options.st:\t", options.st
            print "options.lo:\t", options.lo
            print "options.ch:\t", options.ch
    # change time string to UTCDateTime object. This is done last, so it's
    # only necessary once, no matter if -t or -s -e
    try:
        options.start = UTCDateTime(options.start)
        options.end = UTCDateTime(options.end)
    except:
        print "Given time string not compatible with ObsPy UTCDateTime method."
        help()
        sys.exit(2)
    if options.debug:
        print "Now it's UTCDateTime:"
        print "options.start", options.start
        print "options.end", options.end
    cwd = os.getcwd()
    # change default datapath if we're in metadata query mode
    if options.metadata and options.datapath == 'obspysod-data':
        options.datapath = os.path.join(cwd, 'obspysod-metadata')
    # parse datapath (check if given absolute or relative)
    if os.path.isabs(options.datapath):
        datapath = options.datapath
    else:
        datapath = os.path.join(cwd, options.datapath)
    # delete data path if -R or --reset args are given at cmdline
    if options.reset:
        # try-except so we don't get an exception if path doesnt exist
        try:
            from shutil import rmtree
            rmtree(datapath)
        except:
            pass
    # if -q oder --query-metadata, do not enter normal obspysod data download
    # operation, but download resp instrument files and dataless seed and quit.
    if options.metadata:
        print "ObsPySOD will download resp and dataless seed instrument " + \
              "files and quit.\n"
        queryMeta(options.west, options.east, options.south, options.north,
                  options.start, options.end, options.nw, options.st,
                  options.lo, options.ch, options.permanent, options.debug)
        return
    # if -u or --update, delete event and catalog pickled objects
    if options.update:
        try:
            os.remove(os.path.join(datapath, 'events.pickle'))
            os.remove(os.path.join(datapath, 'inventory.pickle'))
        except:
            pass
    # Warn that datapath will be created and give list of further options
    if not options.force:
        if not os.path.isdir(datapath):
            if len(sys.argv) == 1:
                print "\nWelcome,"
                print "you provided no options, using all default values will"
                print "download every event that occurred in the last 3 months"
                print "with magnitude > 3 from every available station."
            print "\nObsPySOD will now create the folder %s" % datapath
            print "and possibly download vast amounts of data. Continue?"
            print "Note: you can suppress this message with -f or --force"
            print "Brief help: obspysod -h"
            print "Long help: obspysod -H"
            answer = raw_input("[y/N]> ")
            if answer != "y":
                print "Exiting ObsPySOD."
                sys.exit(2)
        else:
            print "Found existing data folder %s" % datapath
            msg = "Resume download?\nNotes:"
            msg += "- suppress this message with -f or --force\n"
            msg += "- update the event database before resuming download "
            msg += "with -u or --update\n"
            msg += "- reset and redownload everything, including all data, "
            msg += "with -R or --reset\n"
            msg += "Brief help: obspysod -h\n"
            msg += "Long help: obspysod -H"
            print msg
            answer = raw_input("[y/N]> ")
            if answer != "y":
                print "Exiting obspy."
                sys.exit(2)
    # create datapath
    if not os.path.exists(datapath):
        os.mkdir(datapath)
    # start keypress thread, so we can quit by pressing 'q' anytime from now on
    # during the downloads
    done = False
    keypress_thread().start()
    # (1) get events from NERIES-eventservice
    if options.debug:
        print '#############'
        print "options: ", options
        print '#############'
    events = get_events(options.west, options.east, options.south,
                            options.north, options.start, options.end,
                            options.magmin, options.magmax)
    if options.debug:
        print '#############'
        print 'events:'
        print events
        print '#############'
    # (2) get inventory data from ArcLink
    # ArcLink supports wildcard searches like 'R*' for station, but not for
    # network, where it accepts only * or exact network name
    # handle network restrictions: obspysod accepts e.g. R* for network:
    nwcheck = False
    if '*' in options.nw:
    # if '*' in options.nw and options.nw != '*':
        options.nw2 = '*'
        nwcheck = True
    else:
        options.nw2 = options.nw
    # check if the user pressed 'q' while we did d/l eventlists.
    check_quit()
    networks, stations = get_inventory(options.start, options.end, options.nw2,
                                      options.st, options.lo, options.ch,
                                      permanent=options.permanent,
                                      debug=options.debug)
    # networks is a list of all networks and not needed again
    # stations is a list of all stations (nw.st.l.ch, so it includes networks)
    if options.debug:
        print '#############'
        print 'networks(actual network wildcard search is handled internally):'
        print networks
        print 'stations:'
        print stations
        print '#############'
    # (3) Get availability data from IRIS
    # check if the user pressed 'q' while we did d/l the inventory from ArcLink
    check_quit()
    avail = getnparse_availability(west=options.west, east=options.east,
                                   south=options.south, north=options.north,
                                   start=options.start, end=options.end,
                                   nw=options.nw, st=options.st, lo=options.lo,
                                   ch=options.ch, debug=options.debug)
    irisclient = obspy.iris.Client(debug=options.debug)
    # (4) write catalog file, create folders
    headline = "event_id;datetime;origin_id;author;flynn_region;"
    headline += "latitude;longitude;depth;magnitude;magnitude_type;"
    headline += "DataQuality;TimingQualityMin\n" + "#" * 126 + "\n\n"
    hl_eventf = "Station;Data Provider;TQ min;Gaps;Overlaps" + "\n"
    hl_eventf += "#" * 42 + "\n\n"
    catalogfp = os.path.join(datapath, 'catalog.txt')
    catalogfout = open(catalogfp, 'wt')
    catalogfout.write(headline)
    # initialize ArcLink webservice client
    arcclient = obspy.arclink.Client(timeout=5, debug=options.debug)
    mseed = LibMSEED()
    # (5) Loop through events
    # init neriesclient here, need it inside every loop to d/l respective
    # quakeml xml
    neriesclient = obspy.neries.Client()
    for eventdict in events:
        check_quit()
        eventid = eventdict['event_id']
        eventtime = eventdict['datetime']
        if options.debug:
            print '#############'
            print 'event:', eventid
            for key in eventdict:
                print key, eventdict[key]
        # create event info line for catalog file and quakefile
        infoline = eventdict['event_id'] + ';' + str(eventdict['datetime'])
        infoline += ';' + str(eventdict['origin_id']) + ';'
        infoline += eventdict['author'] + ';' + eventdict['flynn_region']
        infoline += ';' + str(eventdict['latitude']) + ';'
        infoline += str(eventdict['longitude']) + ';'
        infoline += str(eventdict['depth']) + ';' + str(eventdict['magnitude'])
        infoline += ';' + eventdict['magnitude_type']
        # create event-folder
        eventdir = os.path.join(datapath, eventid)
        if not os.path.exists(eventdir):
            os.mkdir(eventdir)
        # download quake ml xml
        print "Downloading quakeml xml file for event %s..." % eventid,
        quakeml = neriesclient.getEventDetail(eventid, 'xml')
        quakemlfp = os.path.join(eventdir, 'quakeml.xml')
        quakemlfout = open(quakemlfp, 'wt')
        quakemlfout.write(quakeml)
        quakemlfout.close()
        print "done."
        # init/reset dqsum
        dqsum = 0
        tqlist = []
        # create event file in event dir
        # DQ: all min entries in event folder txt file differently
        # this is handled inside the station loop
        quakefp = os.path.join(eventdir, 'quake.txt')
        quakefout = open(quakefp, 'wt')
        quakefout.write(headline[:97] + "\n" + "#" * 97 + "\n\n")
        quakefout.write(infoline + '\n\n\n')
        quakefout.write(hl_eventf)
        quakefout.flush()
        # (5.1) ArcLink wf data download loop (runs inside event loop)
        # Loop trough stations
        for station in stations:
            check_quit()
            # skip dead networks
            net, sta, loc, cha = station.split('.')
            if net in skip_networks:
                print 'Skipping dead network %s...' % net
                # continue the for-loop to the next iteration
                continue
            # XXX need to change this to using regex
            # and rather inside the arclink fct.
            # ArcLink does not support 'x*' and '*x' searches for networks,
            # done manually here:
            if nwcheck:
                # x* and *x type wildcard searches are supported
                # i guess it's not the best way but I'm trying
                # to get by without re for now
                # if the rest without * is not in net: next iteration
                if options.nw[0] == '*':
                    if options.nw[1:] not in net:
                        continue
                elif options.nw[-1] == '*':
                    if options.nw[:-1] not in net:
                        continue
                # backup behaviour if 'x*x' type search which is not
                # supported occurs automatically: it will just d/l everything
                # no else needed
            # create data file handler
            datafout = os.path.join(eventdir, "%s.mseed" % station)
            if os.path.isfile(datafout):
                print 'Data file for event %s from %s exists, skip...' \
                                                           % (eventid, station)
                continue
            print 'Downloading event %s from ArcLink %s...' \
                                                          % (eventid, station),
            try:
                # catch exception so the d/l continues if only one doesn't work
                arcclient.saveWaveform(filename=datafout, network=net,
                                       station=sta, location=loc, channel=cha,
                                       starttime=eventtime - options.preset,
                                       endtime=eventtime + options.offset)
            except Exception, error:
                print "download error: ",
                print error
                continue
            else:
                # else code will run if try returned no exception!
                # write station name to event info line
                il_quake = station + ';ArcLink;'
                # Quality Control with libmseed
                dqsum += sum(mseed.getDataQualityFlagsCount(datafout))
                # Timing Quality, trying to get all stations into one line in
                # eventfile, and handling the case that some station's mseeds
                # provide TQ data, and some do not
                tq = mseed.getTimingQuality(datafout)
                if tq != {}:
                    tqlist.append(tq['min'])
                    il_quake += str(tq['min'])
                else:
                    il_quake += str('None')
                # finally, gaps&overlaps into quakefile
                # read mseed into stream, use .getGaps method
                st = read(datafout)
                # this code snippet is taken from stream.printGaps since I need
                # gaps and overlaps distinct.
                result = st.getGaps()
                gaps = 0
                overlaps = 0
                for r in result:
                    if r[6] > 0:
                        gaps += 1
                    else:
                        overlaps += 1
                del st
                il_quake += ';%d;%d\n' % (gaps, overlaps)
                quakefout.write(il_quake)
                quakefout.flush()
                # if there has been no Exception, assume d/l was ok
                print "done."
        # (5.2) Iris wf data download loop
        for (net, sta, loc, cha) in avail:
            check_quit()
            # construct filename:
            station = '.'.join((net, sta, loc, cha))
            irisfn = station + '.mseed'
            irisfnfull = os.path.join(datapath, eventid, irisfn)
            if options.debug:
                print 'irisfnfull:', irisfnfull
            if os.path.isfile(irisfnfull):
                print 'Data file for event %s from %s exists, skip...' % \
                                                         (eventid, station)
                continue
            print 'Downloading event %s from IRIS %s...' % (eventid, station),
            try:
                irisclient.saveWaveform(filename=irisfnfull,
                                        network=net, station=sta,
                                        location=loc, channel=cha,
                                        starttime=eventtime - options.preset,
                                        endtime=eventtime + options.offset)
            except Exception, error:
                print "download error: ", error
                continue
            else:
                # if there was no exception, the d/l should have worked
                print 'done.'
                # data quality handling for iris
                # write station name to event info line
                il_quake = station + ';IRIS;'
                # Quality Control with libmseed
                dqsum += sum(mseed.getDataQualityFlagsCount(irisfnfull))
                # Timing Quality, trying to get all stations into one line in
                # eventfile, and handling the case that some station's mseeds
                # provide TQ data, and some do not
                tq = mseed.getTimingQuality(irisfnfull)
                if tq != {}:
                    tqlist.append(tq['min'])
                    il_quake += str(tq['min'])
                else:
                    il_quake += str('None')
                # finally, gaps&overlaps into quakefile
                # read mseed into stream, use .getGaps method
                st = read(irisfnfull)
                # this code snippet is taken from stream.printGaps since I need
                # gaps and overlaps distinct.
                result = st.getGaps()
                gaps = 0
                overlaps = 0
                for r in result:
                    if r[6] > 0:
                        gaps += 1
                    else:
                        overlaps += 1
                del st
                il_quake += ';%d;%d\n' % (gaps, overlaps)
                quakefout.write(il_quake)
                quakefout.flush()
                print "done."
        # write data quality info into catalog file event info line
        if dqsum == 0:
            infoline += ';0 (OK);'
        else:
            infoline += ';' + str(dqsum) + ' (FAIL);'
        # write timing quality into event info line (minimum of all 'min'
        # entries
        if tqlist != []:
            infoline += '%.2f' % min(tqlist) + '\n'
        else:
            infoline += 'None\n'
        # write event info line to catalog file (including QC)
        catalogfout.write(infoline)
        catalogfout.flush()
        # close quake file at end of station loop
        quakefout.close()
    # done with ArcLink, remove ArcLink client
    del arcclient
    # done with iris, remove client
    del irisclient
    # close event catalog info file at the end of event loop
    catalogfout.close()
    done = True
    return


def get_events(west, east, south, north, start, end, magmin, magmax):
    """
    Downloads and saves list of events if not present in datapath.

    Parameters
    ----------
    west : int or float, optional
        Minimum ("left-side") longitude.
        Format: +/- 180 decimal degrees.
    east : int or float, optional
        Maximum ("right-side") longitude.
        Format: +/- 180 decimal degrees.
    south : int or float, optional
        Minimum latitude.
        Format: +/- 90 decimal degrees.
    north : int or float, optional
        Maximum latitude.
        Format: +/- 90 decimal degrees.
    start : str, optional
        Earliest date and time.
    end : str, optional
        Latest date and time.
    magmin : int or float, optional
        Minimum magnitude.
    magmax : int or float, optional
        Maximum magnitude.

    Returns
    -------
        List of event dictionaries.
    """
    eventfp = os.path.join(datapath, 'events.pickle')
    try:
        # b for binary file
        fh = open(eventfp, 'rb')
        events = pickle.load(fh)
        fh.close()
        print "Found eventlist in datapath, skip download."
    except:
        print "Downloading NERIES eventlist...",
        client = obspy.neries.Client()
        # the maximum no of allowed results seems to be not allowed to be too
        # large, but 9999 seems to work, 99999 results in a timeout error in
        # urllib
        events = client.getEvents(min_latitude=south, max_latitude=north,
                                  min_longitude=west, max_longitude=east,
                                  min_datetime=start, max_datetime=end,
                                  min_magnitude=magmin, max_magnitude=magmax,
                                  max_results=9999)
        del client
        # dump events to file
        fh = open(eventfp, 'wb')
        pickle.dump(events, fh)
        fh.close()
        print "done."
    print("Received %d event(s) from NERIES." % (len(events)))
    return events


def get_inventory(start, end, nw, st, lo, ch, permanent, debug=False):
    """
    Searches the ArcLink inventory for available networks and stations.

    Parameters
    ----------
    start : str, optional
        ISO 8601-formatted, in UTC: yyyy-MM-dd['T'HH:mm:ss].
        e.g.: "2002-05-17" or "2002-05-17T05:24:00"
    end : str, optional
        ISO 8601-formatted, in UTC: yyyy-MM-dd['T'HH:mm:ss].
        e.g.: "2002-05-17" or "2002-05-17T05:24:00"

    Returns
    -------
        A tuple of (networks, stations)
    """
    inventoryfp = os.path.join(datapath, 'inventory.pickle')
    try:
        # first check if inventory data has already been downloaded
        fh = open(inventoryfp, 'rb')
        inventory = pickle.load(fh)
        fh.close()
        print "Found inventory data in datapath, skip download."
    except:
        arcclient = obspy.arclink.client.Client()
        print "Downloading ArcLink inventory data...",
        # restricted = false, we don't want restricted data
        # permanent is handled via command line flag
        if debug:
            print "permanent flag: ", permanent
        try:
            inventory = arcclient.getInventory(network=nw, station=st,
                                               location=lo, channel=ch,
                                               starttime=start, endtime=end,
                                               permanent=permanent,
                                               restricted=False)
        except Exception, error:
            print "download error: ", error
            print "ArcLink returned no stations."
            # return empty result in the form of (networks, stations)
            return ([], [])
        else:
            # dump inventory to file so we can quickly resume d/l if obspysod
            # runs in the same dir more than once
            fh = open(inventoryfp, 'wb')
            pickle.dump(inventory, fh)
            fh.close()
            print "done."
    # XXX change this
    if debug:
        print "inventory inside get_inventory(): ", inventory
    networks = sorted([i for i in inventory.keys() if i.count('.') == 0])
    stations = sorted([i for i in inventory.keys() if i.count('.') == 3])
    # networks is a list of all networks and not needed again
    print("Received %d network(s) from ArcLink." % (len(networks)))
    print("Received %d channels(s) from ArcLink." % (len(stations)))
    return (networks, stations)


def getnparse_availability(west, east, south, north, start, end, nw, st, lo,
                           ch, debug):
    """
    Downloads and parses IRIS availability XML.
    """
    irisclient = obspy.iris.Client(debug=debug)
    try:
        # create data path:
        if not os.path.isdir(datapath):
            os.mkdir(datapath)
        # try to load availability file
        availfp = os.path.join(datapath, 'availability.pickle')
        fh = open(availfp, 'rb')
        avail_list = pickle.load(fh)
        fh.close()
        print "Found IRIS availability in datapath, skip download."
        return avail_list
    except:
        print "Downloading IRIS availability data...",
        try:
            result = irisclient.availability(
                                     network=nw, station=st, location=lo,
                                     channel=ch, starttime=UTCDateTime(start),
                                     endtime=UTCDateTime(end), minlat=south,
                                     maxlat=north, minlon=west, maxlon=east,
                                     output='xml')
        except Exception, error:
            print "\nIRIS returned to matching stations."
            if debug:
                print "\niris client error: ", error
            # return an empty list (iterable empty result)
            return []
        else:
            print "done."
            print "Parsing IRIS availability xml to obtain nw.st.lo.ch...",
            availxml = etree.fromstring(result)
            if debug:
                print 'availxml:\n', availxml
            stations = availxml.xpath('Station')
            # I will construct a list of tuples of stations of the form:
            # [(net,sta,cha,loc), (net,sta,loc,cha), ...]
            avail_list = []
            for station in stations:
                net = station.values()[0]
                sta = station.values()[1]
                channels = station.xpath('Channel')
                for channel in channels:
                    loc = channel.values()[1]
                    cha = channel.values()[0]
                    if debug:
                        print '#### station/channel: ####'
                        print 'net', net
                        print 'sta', sta
                        print 'loc', loc
                        print 'cha', cha
                    # strip it so we can use it to construct nicer filenames
                    # as well as to construct a working IRIS ws query
                    avail_list.append((net.strip(' '), sta.strip(' '),
                                       loc.strip(' '), cha.strip(' ')))
            # dump availability to file
            fh = open(availfp, 'wb')
            pickle.dump(avail_list, fh)
            fh.close()
            print "done."
            if debug:
                print "avail_list: ", avail_list
            print("Received %d station(s) from IRIS." % (len(stations)))
            print("Received %d channel(s) from IRIS." % (len(avail_list)))
            return avail_list


def queryMeta(west, east, south, north, start, end, nw, st, lo, ch, permanent,
              debug):
    """
    Downloads Resp instrument data and dataless seed files.
    """
    global quit, done
    # start keypress thread, so we can quit by pressing 'q' anytime from now on
    # during the downloads
    done = False
    keypress_thread().start()
    irisclient = obspy.iris.Client(debug=debug)
    arclinkclient = obspy.arclink.client.Client(debug=debug)
    # (1) IRIS: resp files
    # get and parse IRIS availability xml
    avail = getnparse_availability(west=west, east=east, south=south,
                                   north=north, start=start, end=end,
                                   nw=nw, st=st, lo=lo, ch=ch,
                                   debug=debug)
    # stations is a list of all stations (nw.st.l.ch, so it includes networks)
    # loop over all tuples of a station in avail list:
    for (net, sta, loc, cha) in avail:
        check_quit()
        # construct filename
        respfn = '.'.join((net, sta, loc, cha)) + '.resp'
        respfnfull = os.path.join(datapath, respfn)
        if debug:
            print 'respfnfull:', respfnfull
            print 'type cha: ', type(cha)
            print 'length cha: ', len(cha)
            print 'net: %s sta: %s loc: %s cha: %s' % (net, sta, loc, cha)
        if os.path.isfile(respfnfull):
            print 'Resp file for %s exists, skip download...' % respfn
            continue
        print 'Downloading Resp file for %s from IRIS...' % respfn,
        try:
            irisclient.saveResponse(respfnfull, net, sta, loc, cha, start, end,
                                    format='RESP')
        except Exception, error:
            print "\ndownload error: ",
            print error
            continue
        else:
            # if there has been no exception, the d/l should have worked
            print 'done.'
    # (2) ArcLink: dataless seed
    # get ArcLink inventory
    networks, stations = get_inventory(start, end, nw, st, lo, ch,
                                       permanent=permanent, debug=debug)
    # loop over stations to d/l every dataless seed file...
    # skip dead ArcLink networks
    skip_networks = ['AI', 'BA']
    for station in stations:
        check_quit()
        # skip dead networks
        net, sta, loc, cha = station.split('.')
        if net in skip_networks:
            print 'Skipping dead network %s...' % net
            # continue the for-loop to the next iteration
            continue
        # construct filename
        dlseedfn = '.'.join((net, sta, loc, cha)) + '.seed'
        dlseedfnfull = os.path.join(datapath, dlseedfn)
        # ArcLink does not support 'x*' and '*x' searches for networks,
        # done manually here: not done here anymore right now.
        # XXX need to change this, use regex instead...
        # and rather inside the arclink get_inventory fct.
        # create data file handler
        dlseedfnfull = os.path.join(datapath, "%s.mseed" % station)
        if os.path.isfile(dlseedfnfull):
            print 'Dataless file for %s exists, skip download...' % dlseedfn
            continue
        print 'Downloading dataless seed file for %s from ArcLink...' \
                                                                  % dlseedfn,
        try:
            # catch exception so the d/l continues if only one doesn't work
            arclinkclient.saveResponse(dlseedfnfull, net, sta, loc, cha,
                                       start, end, format='SEED')
        except Exception, error:
            print "download error: ",
            print error
            continue
        else:
            # if there has been no exception, the d/l should have worked
            print 'done.'
    done = True


def getFolderSize(folder):
    """
    Returns the size of a folder in bytes.
    """
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size


def printWrap(left, right, l_width=14, r_width=61, indent=2, separation=3):
    """
    Formats and prints a text output into 2 columns. Needed for the custom
    (long) help.
    """
    lefts = wrap(left, width=l_width)
    rights = wrap(right, width=r_width)
    results = []
    for l, r in izip_longest(lefts, rights, fillvalue=''):
        results.append('{0:{1}}{2:{5}}{0:{3}}{4}'.format('', indent, l,
                                                 separation, r, l_width))
    print "\n".join(results)
    return


def help():
    """
    Print more help.
    """
    print "\nObsPySOD: ObsPy Standing Order for Data tool"
    print "============================================\n\n"
    print "The CLI allows for different flavors of usage, in short:"
    print "--------------------------------------------------------\n"
    printWrap("e.g.:", "obspysod.py -r <west>/<east>/<south>/<north> -t " + \
          "<start>/<end> -m <min_mag> -M <max_mag> -i <nw>.<st>.<l>.<ch>")
    printWrap("e.g.:", "obspysod.py -y <min_lon> -Y <max_lon> -x <min_lat>" + \
       "-X <max_lat> -s <start> -e <end> -P <datapath> -o <offset> --reset -f")
    print "\n\nYou may (no mandatory options):"
    print "-------------------------------\n"
    print "* specify a geographical rectangle:\n"
    printWrap("Default:", "no constraints.")
    printWrap("Format:", "+/- 90 decimal degrees for latitudinal limits,")
    printWrap("", "+/- 180 decimal degrees for longitudinal limits.")
    print
    printWrap("-r[--rect]",
            "<min.longitude>/<max.longitude>/<min.latitude>/<max.latitude>")
    printWrap("", "e.g.: -r -15.5/40/30.8/50")
    print
    printWrap("-x[--lonmin]", "<min.latitude>")
    printWrap("-X[--lonmax]", "<max.longitude>")
    printWrap("-y[--latmin]", "<min.latitude>")
    printWrap("-Y[--latmax]", "<max.latitude>")
    printWrap("", "e.g.: -x -15.5 -X 40 -y 30.8 -Y 50")
    print "\n"
    print "* specify a timeframe:\n"
    printWrap("Default:", "the last 3 months")
    printWrap("Format:", "Any obspy.core.UTCDateTime recognizable string.")
    print
    printWrap("-t[--time]", "<start>/<end>")
    printWrap("", "e.g.: -t 2007-12-31/2011-01-31")
    print
    printWrap("-s[--start]", "<starttime>")
    printWrap("-e[--end]", "<endtime>")
    printWrap("", "e.g.: -s 2007-12-31 -e 2011-01-31")
    print "\n"
    print "* specify a minimum and maximum magnitude:\n"
    printWrap("Default:", "minimum magnitude 3, no maximum magnitude.")
    printWrap("Format:", "Integer or decimal.")
    print
    printWrap("-m[--magmin]", "<min.magnitude>")
    printWrap("-M[--magmax]", "<max.magnitude>")
    printWrap("", "e.g.: -m 4.2 -M 9")
    print "\n"
    print "* specify a station restriction:\n"
    printWrap("Default:", "no constraints.")
    printWrap("Format:", "Any station code, may include wildcards.")
    print
    printWrap("-i[--identity]", "<nw>.<st>.<l>.<ch>")
    printWrap("", "e.g. -i IU.ANMO.00.BH* or -i *.*.?0.BHZ")
    print
    printWrap("-N[--network]", "<network>")
    printWrap("-S[--station]", "<station>")
    printWrap("-L[--location]", "<location>")
    printWrap("-C[--channel]", "<channel>")
    printWrap("", "e.g. -N IU -S ANMO -L 00 -C BH*")
    print "\n\n* specify additional options:\n"
    printWrap("-n[--no-temporary]", "")
    printWrap("", "Instead of downloading both temporary and permanent " + \
          "networks (default), download only permanent ones.")
    print
    # hopefully this will be automatically with taupe arrival times later
    printWrap("-p[--preset]", "<preset>")
    printWrap("", "Time parameter given in seconds which determines how " + \
        "close the data will be cropped before event origin time. Default: 0")
    print
    printWrap("-o[--offset]", "<offset>")
    printWrap("", "Time parameter given in seconds which determines how " + \
              "close the data will be cropped after the event origin time.")
    print
    printWrap("-q[--query-resp]", "")
    printWrap("", "Instead of downloading seismic data, download " + \
              "instrument response files.")
    print
    printWrap("-P[--datapath]", "<datapath>")
    printWrap("", "Specify a different datapath, do not use do default one.")
    print
    printWrap("-R[--reset]", "")
    printWrap("", "If the datapath is found, do not resume previous " + \
              "downloads as is the default behaviour, but redownload " + \
              "everything. Same as deleting the datapath before running " + \
              "ObsPySOD.")
    print
    printWrap("-u[--update]", "")
    printWrap("", "Update the event database if ObsPySOD runs on the " + \
              "same directory for a second time.")
    print
    printWrap("-f[--force]", "")
    printWrap("", "Skip working directory warning (auto-confirm folder" + \
              " creation).")
    print "\nType obspysod.py -h for a list of all long and short options."
    # XXX need better examples
    print "\n\nExamples:"
    print "---------\n"
    printWrap("Alps region, minimum magnitude of 4.2:",
              "obspysod.py -r 5/16.5/45.75/48 -t 2007-01-13T08:24:00/" + \
              "2011-02-25T22:41:00 -m 4.2")
    print
    printWrap("Sumatra region, Christmas 2004, different timestring, " + \
              "mind the quotation marks:",
              "obspysod.py -r 90/108/-7/7 -t \"2004-12-24 01:23:45/" + \
              "2004-12-26 12:34:56\" -m 9")
    print
    printWrap("Mount Hochstaufen area(Ger/Aus), default minimum magnitude:",
              "obspysod.py -r 12.8/12.9/47.72/47.77 -t 2001-01-01/2011-02-28")
    print
    return


if __name__ == "__main__":
    """
    global quit
    # I could not get my interrupt handler to work. The plan was to capture
    # ^c, prevent the program from quitting immediately, finish the last
    # download and then quit. Perhaps someone could pick up on this.
    # It almost worked, but select.select couldn't restart after receiving
    # SIGINT. I have been told that's a bad design in the python bindings, but
    # that's above me. Had to give up.
    # Meanwhile, I think the method with 2 threads and pressing "q" instead
    # works fine.
    # The implementation uses class keypress_thread and function getkey(see
    # above).
    def interrupt_handler(signal, frame):
        global quit
        if not quit:
            print "You pressed ^C (SIGINT)."
            msg = "Obspysod will finish downloading and saving the last file"+\
                    " and quit gracefully."
            print msg
            print "Press ^C again to interrupt immediately."
        else:
            msg = "Interrupting immediately. The last file will most likely"+ \
                    " be corrupt."
            sys.exit(2)
        quit = True
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.siginterrupt(signal.SIGINT, False)
    """
    global quit, done
    quit = False
    begin = time.time()
    status = main()
    size = getFolderSize(datapath)
    elapsed = time.time() - begin
    print "Downloaded %d bytes in %d seconds." % (size, elapsed)
    # sorry for the inconvenience, AFAIK there is no other way to quit the
    # second thread since getkey is waiting for input:
    print "Done, press any key to quit."
    # pass the return of main to the command line.
    sys.exit(status)
