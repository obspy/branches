#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Obspy Standing Order for Data. Meant to be used from the shell.
This has been part of a Bachelor's Thesis at the University of Munich.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""

import sys
import os
import pickle
# do not need signal, no ^c handling - quit d/l with q now
#import signal
from ConfigParser import ConfigParser
from optparse import OptionParser
from obspy.core import UTCDateTime
from obspy.core import read
import obspy.neries
import obspy.arclink
import obspy.iris
from obspy.mseed.libmseed import LibMSEED
from BeautifulSoup import BeautifulSoup

# need threading to be able to capture keypress event without a GUI like
# tkinter or pyqt and run the main loop at the same time.
# This should run cross-plattform... 
import threading, termios
TERMIOS = termios
# need a lock for the global quit variable which is used in two threads
lock = threading.RLock()


class keypress_thread (threading.Thread):
    """
    This class will run as a second thread to capture keypress events
    """
    global quit
    def run (self):
        global quit
        print 'Keypress capture thread initialized...'
        print "Press 'q' at any time to finish downloading and saving the \
last file and then quit."
        while True:
            c = getkey()
            print c
            if c == 'q':
                with lock:
                    quit = True
                print "You pressed q."
                print "Obspysod will finish downloading and saving the last file and \
quit gracefully."
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


def main():
    """
    Main function to run as a dedicated program.
    """
    global datapath, cwd
    # dead networks
    skip_networks = ['AI', 'BA']
    # create ConfigParser object.
    # set variable names as dict keys, default values as _STRINGS_!
    # you don't need to provide every possible option here, just the ones with
    # default values
    # need to provide default start and end time, otherwise
    # obspy.arclink.getInventory will raise an error if the user does not
    # provide start and end time
    config = ConfigParser({'magmin': '3',
                           'dt': '10',
                           'start': '2011-01-01',
                           'end': '2011-05-01',
                           'preset': '0',
                           'offset': '20',
                           'datapath': 'obspysod-data',
                           'nw':'*',
                           'st':'*',
                           'lo':'*',
                           'ch':'*',
                          })

    # read config file, if it exists, possibly overriding defaults as set above
    config.read('.obspysodrc')

    # create command line option parser
    # parser = OptionParser("%prog [options]" + __doc__.rstrip())
    parser = OptionParser("%prog [options]")

    # configure command line options
    # action=".." sagt was er machen soll: store_true saved bool TRUE,
    # store_false saved bool FALSE, store saved string, jeweils in die var. die
    # in dest="..var.." angeg. ist
    # * you need to provide every possible option here.
    # reihenfolge wird eingehalten in help msg.
    parser.add_option("-H", "--detailed-help", action="store_true",
                      dest="showhelp", help="Show detailed help and exit")
    parser.add_option("-q", "--query-resp", action="store_true",
                      dest="resp", help="Instead of downloading seismic\
                      data, download resp instrument files.")
    parser.add_option("-P", "--datapath", action="store", dest="datapath",
                      help="The path where obspysod will store the data\
                     (default is ./obspysod-data for the data download mode\
                      and ./obspysod-resp for resp download mode).")
    parser.add_option("-u", "--update", help="Update the event database when\
                      obspysod runs on the same directory a second time in\
                      order to continue data downloading.",
                      action="store_true", dest="update")
    parser.add_option("-R", "--reset", action="store_true",
                      dest="reset", help="If the datapath is found, do not\
                      resume previous downloads as is the default behaviour,\
                      but redownload everything. Same as deleting the datapath\
before running obspysod.")
    parser.add_option("-s", "--starttime", action="store", dest="start",
                      help="Start time")
    parser.add_option("-e", "--endtime", action="store", dest="end",
                      help="End time")
    parser.add_option("-t", "--time", action="store", dest="time",
                      help="Start and End Time as one option delimited by a\
                      slash")
    parser.add_option("-p", "--preset", action="store", dest="preset",
                      help="Time parameter which determines how\
                      close the event data will be cropped before the event")
    parser.add_option("-o", "--offset", action="store", dest="offset",
                      help="Time parameter which determines how\
                      close the event data will be cropped after the event")
    parser.add_option("-m", "--magmin", action="store", dest="magmin",
                      help="Minimum magnitude. Default: 3")
    parser.add_option("-M", "--magmax", action="store", dest="magmax",
                      help="Maximum magnitude")
    parser.add_option("-r", "--rect", action="store", dest="rect",
                      help="Provide rectangle with GMT syntax (alternative to\
                      -x -X -y -Y)")
    parser.add_option("-x", "--latmin", action="store", dest="south",
                      help="Minimum latitude")
    parser.add_option("-X", "--latmax", action="store", dest="north",
                      help="Maximum latitude")
    parser.add_option("-y", "--lonmin", action="store", dest="west",
                      help="Minimum longitude")
    parser.add_option("-Y", "--lonmax", action="store", dest="east",
                      help="Maximum longitude")
    parser.add_option("-i", "--identity", action="store", dest="identity",
    help="Identity code restriction, syntax: nw.st.l.ch (alternative to \
-N -S -L -C)")
    parser.add_option("-N", "--network", action="store", dest="nw",
                      help="Network restriction. Default: *")
    parser.add_option("-S", "--station", action="store", dest="st",
                      help="Station restriction. Default: *")
    parser.add_option("-L", "--location", action="store", dest="lo",
                      help="Location restriction. Default: *")
    parser.add_option("-C", "--channel", action="store", dest="ch",
                      help="Channel restriction. Default: *")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                      help="Skip working directory warning.")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Show debugging information")

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
            print "Either provide the rectangle with GMT syntax, or with -x -X\
 -y -Y, not both."
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
        print "It makes no sense to provide start and end time with -s -e \
and with -t at the same time, but if you do so, -t will override -s -e."
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
        print "It makes no sense to provide station restrictions with -i \
and with -N -S -L -C at the same time, but if you do so, -i will override."
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
        print "Erroneous timeframe given."
        help()
        sys.exit(2)
    if options.debug:
        print "Now it's UTCDateTime:"
        print "options.start", options.start
        print "options.end", options.end
    # parse datapath (check if given absolute or relative)
    cwd = os.getcwd()
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

    # if -q oder --query-resp, do not enter normal obspysod data download
    # operation, but download resp instrument files and quit.
    if options.resp:
        print "Obspysod will download dataless instrument files and quit.\n"
        # we want a different default path for the dataless routine, but the
        # same command line flag -P, so:
        if options.datapath == 'obspysod-data':
            options.datapath = os.path.join(cwd, 'obspysod-resp')
        queryResp(options.west, options.east, options.south, options.north,
                  options.start, options.end, options.nw, options.st,
                  options.lo, options.ch, options.datapath, options.debug)
        sys.exit()
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
            print "obspysod will now create the folder %s" % datapath
            print "and possibly download vast amounts of data. Continue?"
            print "Note: you can suppress this message with -f or --force"
            print "Brief help: obspysod -h"
            print "Long help: obspysod -H"
            answer = raw_input("[y/N]> ")
            if answer != "y":
                print "Exiting obspy."
                sys.exit(2)
        else:
            print "Found existing data folder %s" % datapath
            print "Resume download?"
            print "Notes:"
            print "- suppress this message with -f or --force"
            print "- update the event database before resuming download with\
 -u or --update"
            print "- reset and redownload everything, including all data, with\
 -R or --reset"
            print "Brief help: obspysod -h"
            print "Long help: obspysod -H"
            answer = raw_input("[y/N]> ")
            if answer != "y":
                print "Exiting obspy."
                sys.exit(2)
    # create datapath
    if not os.path.exists(datapath):
        os.mkdir(datapath)

    # start keypress thread, so we can quit by pressing 'q' anytime from now on
    # during the downloads
    keypress_thread().start()
    # get events from NERIES-eventservice
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
    # get inventory data from ARCLINK
    # ARCLINK supports wildcard searches like 'R*' for station, but not for
    # network, where it accepts only * or exact network name
    # handle network restrictions: obspysod accepts e.g. R* for network:
    nwcheck = False
    if '*' in options.nw:
    # if '*' in options.nw and options.nw != '*':
        options.nw2='*'
        nwcheck = True
    else:
        options.nw2=options.nw
    # check if the user pressed 'q' while we did d/l eventlists.
    with lock:
        if quit:
            print "Quitting. To resume the download, just run obspysod \
on the same datapath again."
            sys.exit(0)
    networks, stations = get_inventory(options.start, options.end, options.nw2,
                                      options.st, options.lo, options.ch)
    # networks is a list of all networks and not needed again
    # stations is a list of all stations (nw.st.l.ch, so it includes st.)
    if options.debug:
        print '#############'
        print 'networks:'
        print networks
        print 'stations:'
        print stations
        print '#############'
    #
    # write catalog file, create folders and d/l data
    #
    headline = 'event_id\tdatetime\torigin_id\tauthor\tflynn_region\t\
latitude\tlongitude\tdepth\tmagnitude\tmagnitude_type\tDataQuality\t\
TimingQualityMin\n########\t########\t#########\t######\t############\t\
########\t#########\t#####\t#########\t##############\t#######\t#######\n\n'
    hl_eventf =  'station\t\tTQ min\tGaps\tOverlaps'+'\n'
    hl_eventf += '#######\t\t######\t####\t########\n\n'
    catalogfp = os.path.join(datapath, 'catalog.txt')
    catalogfout = open(catalogfp, 'wt')
    catalogfout.write(headline)
    # Loop through events
    for eventdict in events:
        eventid = eventdict['event_id']
        # eventtime = UTCDateTime(eventdict['datetime'])
        # changed this since all neries methods now return UTCDateTime object
        eventtime = eventdict['datetime']
        if options.debug:
            print '#############'
            print 'event:', eventid
            for key in eventdict:
                print key, eventdict[key]
        # create event info line for catalog file and quakefile
        infoline = eventdict['event_id'] + '\t' + str(eventdict['datetime'])
        infoline += '\t' + str(eventdict['origin_id']) + '\t'
        infoline += eventdict['author'] + '\t' + eventdict['flynn_region'] + '\t'
        infoline += str(eventdict['latitude']) + '\t' + str(eventdict['longitude']) + '\t'
        infoline += str(eventdict['depth']) + '\t' + str(eventdict['magnitude']) + '\t'
        infoline += eventdict['magnitude_type'] + '\t'
        # create event-folder
        eventdir = os.path.join(datapath, eventid)
        if not os.path.exists(eventdir):
            os.mkdir(eventdir)
        client = obspy.arclink.Client(timeout=5, debug=options.debug)
        mseed = LibMSEED()
        # init/reset dqsum
        dqsum = 0
        tqlist = []
        # create event file in event dir
        # DQ: all min entries in event folder txt file differently
        # this is handled inside the station loop
        quakefp = os.path.join(eventdir, 'quake.txt')
        quakefout = open(quakefp, 'wt')
        quakefout.write(headline)
        quakefout.write(infoline + '\n\n')
        quakefout.write(hl_eventf)
        quakefout.flush()
        # arclink wf data download loop
        # Loop trough stations
        for station in stations:
            with lock:
                if quit:
                    print "Quitting. To resume the download, just run obspysod \
on the same datapath again (using the same command line arguments)."
                    sys.exit(0)
            # skip dead networks
            net, sta, loc, cha = station.split('.')
            if net in skip_networks:
                print 'Skipping dead network %s ...' % net
                # continue the for-loop to the next iteration
                continue
            # ArcLink does not support 'x*' and '*x' searches for networks, do it
            # manually here:
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
            # save waveform dataless seed for available stations in inventory
            # create data file handler
            datafout = os.path.join(eventdir, "%s.mseed" % station)
            if os.path.isfile(datafout):
                print 'Data file for event %s from %s exists, \
skip download...' % (eventid, station)
                continue
            print 'Downloading event %s from %s ...' % (eventid, station),
            try:
                # catch exception so the d/l continues if only one doesn't work
                client.saveWaveform(datafout, net, sta, loc, cha, eventtime -
                                    options.preset, eventtime + options.offset)
            except Exception, error:
                print "download error: ",
                print error
                continue
            else:
                # else code will run if try returned no exception!
                # write station name to event info line
                il_quake = station + '\t'
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
                    il_quake +=str('None')
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
                il_quake += '\t%d\t%d\n' % (gaps, overlaps)
                quakefout.write(il_quake)
                quakefout.flush()
                # if there has been no Exception, assume d/l was ok
                print "done."
        # write data quality info into event info line
        if dqsum == 0:
            infoline+= '0 (OK)\t'
        else:
            infoline+= str(dqsum) + ' (FAIL)\t'
        # write timing quality into event info line (minimum of all 'min'
        # entries
        if tqlist != []:
            infoline += '%.2f' % min(tqlist) + '\n'
        else:
            infoline += 'None\n'
        # write event info line to catalog file (including QC)
        catalogfout.write(infoline)
        catalogfout.flush()
        del client
        del mseed
        # close quake and catalog files at end of station loop and event loop,
        # respectively
        quakefout.close()
    catalogfout.close()
    print "All done."


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
        List of event dictionaries or quakeml string.
    """
    eventfp = os.path.join(datapath, 'events.pickle')
    try:
        # b for binary file
        fh = open(eventfp, 'rb')
        events = pickle.load(fh)
        fh.close()
        print "Found eventlist in datapath, skip download."
    except:
        print "Downloading NERIES eventlist..."
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
    print("Received %d event(s)." % (len(events)))
    return events


def get_inventory(start, end, nw, st, lo, ch):
    """
    Searches the arclink inventory for available networks and stations.

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
        print "Downloading ARCLINK inventory data..."
        client = obspy.arclink.Client()
        # "restricted = false, permanent = True" so we only get data that is
        # permanent and public

        inventory = client.getInventory(network=nw, station=st, location=lo,
                                    channel=ch, starttime=start, endtime=end,
                                        permanent=True, restricted=False)
        del client
        # dump inventory to file so we can quickly resume d/l if obspysod runs
        # in the same dir more than once
        fh = open(inventoryfp, 'wb')
        pickle.dump(inventory, fh)
        fh.close()
    # noch anschauen wie genau das funktioniert...!
    networks = sorted([i for i in inventory.keys() if i.count('.') == 0])
    stations = sorted([i for i in inventory.keys()
                            if i.count('.') == 3 and i[-3:].startswith('BH')])
    print("Received %d network(s)" % (len(networks)))
    print("Received %d station(s)" % (len(stations)))
    return (networks, stations)


def availability(start, end, nw, st, lo, ch):
    """
    Searches the IRIS inventory for available networks and stations.
    """
    client = obspy.iris.Client()
    iris_avail = client.availability


def queryResp(west, east, south, north, start, end, nw, st, lo, ch,
                  datapath, debug):
    """
    Downloads Resp instrument data.
    """
    # start keypress thread, so we can quit by pressing 'q' anytime from now on
    # during the downloads
    keypress_thread().start()
    print "Downloading IRIS availability data..."
    client = obspy.iris.Client()
    iris_avail = client.availability(network=nw, station=st, location=lo,
                                     channel=ch, starttime=UTCDateTime(start),
                                     endtime=UTCDateTime(end), minlat=south,
                                     maxlat=north, minlon=west, maxlon=east,
                                     output='xml')
    print "...done"
    if debug:
        print 'datapath:', datapath
        print 'iris_avail:', iris_avail
    # resp file download loop:
    # create dataless path:
    if not os.path.isdir(datapath):
        os.mkdir(datapath)
    with lock:
        if quit:
            print "Quitting. To resume the download, just run obspysod \
on the same datapath again."
            sys.exit(0)
    print "Wrapping IRIS availability xml to obtain nw.st.lo.ch...",
    soup = BeautifulSoup(iris_avail)
    print "done."
    # wrap xml file for net,sta,cha,loc:
    for station in soup.findAll('station'):
        net = str(station.attrs[0][1])
        sta = str(station.attrs[1][1])
        for channel in station.findAll('channel'):
            cha = str(channel.attrs[0][1])
            loc = str(channel.attrs[1][1])
            if debug:
                print '#### station/channel: ####'
                print 'net', net
                print 'sta', sta
                print 'loc', loc
                print 'cha', cha
            # now it's time to d/l our response file since inside this loop, we
            # iterate all individual instruments:
            # construct filename:
            with lock:
                if quit:
                    print "Quitting. To resume the download, just run obspysod\
 on the same datapath again."
                    sys.exit(0)
            respfn = '.'.join((net.strip(' '), sta.strip(' '), loc.strip(' '),
                               cha.strip(' '))) + '.resp'
            respfnfull = os.path.join(datapath, respfn)
            if debug:
                print 'respfnfull:', respfnfull
            if os.path.isfile(respfnfull):
                print 'Resp File for %s exists, skip download...' % respfn
                continue
            print 'Downloading Resp File for %s...' % respfn,
            try:
                client.saveResponse(respfnfull, net, sta, loc, cha, start, end,
                                    format='RESP')
            except Exception, error:
                print "download error: ",
                print error
                continue
            else:
                # if there has been no exception, the d/l should have worked
                print 'done.'
    del client


def help():
    """
    Print detailed help.
    """
    print "\nobspysod - seismological standing order for data based on obspy."
    print "usage: obspysod -r <west>/<east>/<south>/<north> -t <start>/<end> -m <magnitude>"
    print "\nYou need to:"
    print "------------\n"
    print "* specify a geographical rectangle"
    print "\t -r[--rect] \t<min.longitude>/<max.longitude>/<min.latitude>/<max.latitude>"
    print "\t Format: +/- 90 decimal degrees for latitudinal limits,"
    print "\t         +/- 180 decimal degrees for longitudinal limits."
    print "\t         e.g.: -r -15.5/40/30.8/50\n"
    print "* specify a timeframe:"
    print "\t -t[--time] \t<start>/<end>"
    print "\t Format: Any obspy.core.UTCDateTime recognizable string,"
    print "\t         e.g.: -t 2007-12-31T12:23:34.5/2011-01-31T18:23:34.5\n"
    print "* specify a minimum magnitude:"
    print "\t -m[--mag] \t<magnitude>"
    print "\t Format: Integer or decimal,"
    print "\t         e.g.: -m 4.2\n"
    print "Examples:"
    print "---------\n"
    print "* Alps region, minimum magnitude of 4.2:"
    print "  obspysod -r 5/16.5/45.75/48 -t 2007-01-13T08:24:00/2011-02-25T22:41:00 -m 4.2"
    print "* Sumatra region, Christmas 2004, different timestring, mind the quotation marks:"
    print "  obspysod -r 90/108/-7/7 -t \"2004-12-24 01:23:45/2004-12-26 12:34:56\" -m 9"
    print "* Mount Hochstaufen area (Germany/Austria), no minimum magnitude:"
    print "  obspysod -r 12.8/12.9/47.72/47.77 -t 2001-01-01/2011-02-28\n"


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
            print "Obspysod will finish downloading and saving the last file and \
quit gracefully."
            print "Press ^C again to interrupt immediately."
        else:
            print "Interrupting immediately. The last file will most likely \
be corrupt."
            sys.exit(2)
        quit = True
    signal.signal(signal.SIGINT, interrupt_handler)
    signal.siginterrupt(signal.SIGINT, False)
    """
    quit = False
    status = main()
    # pass the return of main to the command line.
    sys.exit(status)
