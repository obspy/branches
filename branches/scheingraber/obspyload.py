#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ObsPyLoad: ObsPy Seismic Data Downloader tool. Meant to be used from the shell.
This has been part of a Bachelor's Thesis at the University of Munich.

:copyright:
    The ObsPy Development Team (devs@obspy.org).
    Developed by Chris Scheingraber.
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/licenses/gpl-3.0-standalone.html)
"""

#############################################
# IMPORT SECTION as described in the thesis #
#############################################
# (\\label{lst:importbegin})
import sys
import os
import operator
import re
import fnmatch
import time
import pickle
# do not need signal, no ^c handling - quit d/l with q now.
# left the remainders in the code since it would be nicer to have 1 thread
# and real ^c handling - perhaps someone will pick up on this, had to give up
#import signal
# using threads to be able to capture keypress event without a GUI like
# tkinter or pyqt and run the main loop at the same time.
# this only works on posix style unix
windows = sys.platform.startswith('win')
if not windows:
    import threading
    import termios
    TERMIOS = termios
    # need a lock for the global quit variable which is used in two threads
    lock = threading.RLock()
from ConfigParser import ConfigParser
from optparse import OptionParser
from obspy.core import UTCDateTime, read
import obspy.neries
import obspy.arclink
import obspy.iris
from obspy.mseed.libmseed import LibMSEED
from lxml import etree
from obspy.taup import taup
# using these modules to wrap the custom(long) help function
from textwrap import wrap
from itertools import izip_longest
try:
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import scipy.ndimage
except Exception, error:
    print error
    print "Missing dependencies, no plotting available."
    pass

# (\\label{lst:abbr})
### may use these abbreviations ###
# comments:                       #
# d/l: download                   #
# wf: waveform                    #
#                                 #
# variable/object names:          #
# net: network                    #
# sta: station                    #
# loc: location                   #
# cha: channel                    #
# *fp: file pointer               #
# *fh: file handler               #
# *fout: file out                 #
# *fin: file in                   #
# il: info line                   #
# hl: headline                    #
# plt*: plot                      #
###################################

######################################################
# KEYPRESS-THREAD SECTION as described in the thesis #
######################################################
# (\\label{lst:keypresswin})
# this is to support windows without changing the rest of the code
if windows:
    class keypress_thread():
        """
        Empty class, for windows support.
        """
        def __init__(self):
            print "Detected windows, no keypress-thread started."

        def start(self):
            print "No 'q' key support on windows."

    def check_quit():
        """
        Does nothing, for windows support.
        """
        return
# (\\label{lst:keypress})
else:
    class keypress_thread (threading.Thread):
        """
        This class will run as a second thread to capture keypress events
        """
        global quit, done

        def run(self):
            global quit, done
            msg = 'Keypress capture thread initialized...\n'
            msg += "Press 'q' at any time to finish " \
            + "the file in progress and quit."
            print msg
            while not done:
                c = getkey()  # (\\label{lst:getkeycall})
                print c
                if c == 'q' and not done:
                    with lock:  # (\\label{lst:lock})
                        quit = True
                    print "You pressed q."
                    msg = "ObsPyLoad will finish downloading and saving the " \
                    + "last file and quit gracefully."
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
                "ObsPyLoad again, using the same arguments."
                print msg
                sys.exit(0)
# (\\label{lst:main})
####################################################
# MAIN FUNCTION SECTION as described in the thesis #
####################################################


def main():
    """
    Main function to run as a dedicated program.
    """

    global datapath, quit, done, skip_networks
    # dead networks deactivated for now
    skip_networks = []
    # if hardcoded skip networks are ok, uncomment this line:
    # skip_networks = ['AI', 'BA']
    ##############################################################
    # CONFIG AND OPTIONPARSER SECTION as described in the thesis #
    ##############################################################
    # create ConfigParser object.
    # set variable names as dict keys, default values as _STRINGS_!
    # you don't need to provide every possible option here, just the ones with
    # default values
    # need to provide default start and end time, otherwise
    # obspy.arclink.getInventory will raise an error if the user does not
    # provide start and end time
    # default for start is three months ago, end is now
    # default offset is 80 min, preset 5min, default velocity model is 'iasp91'
    config = ConfigParser({'magmin': '3',  # (\\label{lst:configstart})
                           'dt': '10',
                           'start': str(UTCDateTime.utcnow()
                                        - 60 * 60 * 24 * 30 * 3),
                           'end': str(UTCDateTime.utcnow()),
                           'preset': '300',
                           'offset': '4800',
                           'datapath': 'obspyload-data',
                           'model': 'iasp91',
                           'phases': 'P,S',
                           'nw': '*',
                           'st': '*',
                           'lo': '*',
                           'ch': '*',
                          })  # (\\label{lst:configend})

    # read config file, if it exists, possibly overriding defaults as set above
    config.read('~/.obspyloadrc')

    # create command line option parser
    # parser = OptionParser("%prog [options]" + __doc__.rstrip())
    parser = OptionParser("%prog [options]")  # (\\label{lst:optionparse})

    # configure command line options
    # action=".." tells OptionsParser what to save:
    # store_true saves bool TRUE,
    # store_false saves bool FALSE, store saves string; into the variable
    # given with dest="var"
    # * you need to provide every possible option here.
    # reihenfolge wird eingehalten in help msg. # (\\label{lst:optionstart})
    parser.add_option("-H", "--more-help", action="store_true",
                      dest="showhelp", help="Show explanatory help and exit.")
    helpmsg = "Instead of downloading seismic data, download metadata: " + \
              "resp instrument and dataless seed files."
    parser.add_option("-q", "--query-metadata", action="store_true",
                      dest="metadata", help=helpmsg)
    helpmsg = "The path where ObsPyLoad will store the data (default is " + \
              "./ObsPyLoad-data for the data download mode and " + \
              "./ObsPyLoad-metadata for metadata download mode)."
    parser.add_option("-P", "--datapath", action="store", dest="datapath",
                      help=helpmsg)
    helpmsg = "Update the event database when ObsPyLoad runs on the same " + \
              "directory a second time in order to continue data downloading."
    parser.add_option("-u", "--update", help=helpmsg,
                      action="store_true", dest="update")
    helpmsg = "If the datapath is found, do not resume previous downloads " + \
              "as is the default behaviour, but redownload everything. " + \
              "Same as deleting the datapath before running ObsPyLoad."
    parser.add_option("-R", "--reset", action="store_true",
                      dest="reset", help=helpmsg)
    parser.add_option("-s", "--starttime", action="store", dest="start",
                      help="Start time. Default: 3 months ago.")
    parser.add_option("-e", "--endtime", action="store", dest="end",
                      help="End time. Default: now.")
    parser.add_option("-t", "--time", action="store", dest="time",
                      help="Start and End Time delimited by a slash.")
    helpmsg = "Velocity model for arrival time calculation used to crop " + \
              "the data, either 'iasp91' or 'ak135'. Default: 'iasp91'."
    parser.add_option("-v", "--velocity-model", action="store", dest="model",
                      help=helpmsg)
    helpmsg = "Time parameter in seconds which determines how close the " + \
            "event data will be cropped before the calculated arrival " + \
            "time. Default: 5 minutes."
    parser.add_option("-p", "--preset", action="store", dest="preset",
                      help=helpmsg)
    helpmsg = "Time parameter in seconds which determines how close the " + \
            "event data will be cropped after the calculated arrival time." + \
            " Default: 80 minutes."
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
    helpmsg = "Instead entering the normal download procedure, read the " + \
              "file exceptions.txt in the datapath, in which all " + \
              "errors ObsPyLoad encountered while downloading are saved. " + \
              "This mode will try to download the data from every " + \
              "station that returned an error other than 'no data " + \
              "available' last time."
    parser.add_option("-E", "--exceptions", action="store_true",
                      dest="exceptions", help=helpmsg)
    helpmsg = "For each event, create one plot with the data from all " + \
              "stations together with theoretical arrival times. You may " + \
              "provide the internal plotting resolution: e.g. " + \
              "-I 900x600x5. This gives you a resolution of 900x600, " + \
              "and 5 units broad station columns. If -I d, " + \
              "or -I default, the default of " + \
              "1200x800x1 will be used. If this parameter is not " + \
              "passed to ObsPyLoad at all, no plots will be created." + \
              " You may additionally specify the timespan of the plot " + \
              "after event origin time in minutes: e.g. for timespan " + \
              "lasting 30 minutes: -I 1200x800x1/30 (or -I d/30). The " + \
              "default timespan is 100 minutes. The final output file " + \
              "will be in pdf format."
    parser.add_option("-I", "--plot", action="store", dest="plt",
                      help=helpmsg)
    helpmsg = "When creating the plot, download all the data needed to " + \
              "fill the rectangular area of the plot. Note: depending on " + \
              "your options, this will approximately double the data " + \
              "download volume (but you'll end up with nicer plots ;-))."
    parser.add_option("-F", "--fill-plot", action="store_true", dest="fill",
                      help=helpmsg)
    helpmsg = "Specify phases for which the theoretical arrival times " + \
              "should be plotted on top if creating the data plot(see " + \
              "above, -I option). Usage: -a phase1,phase2,(...)." + \
              " Default: -a P,S. See the long help for available phases. " + \
              "To plot all available phases, use -a all. If you just " + \
              "want to plot the data and no phases, use -a none."
    parser.add_option("-a", "--phases", action="store", dest="phases",
                      help=helpmsg)
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Show debugging information.")
    # (\\label{lst:optionend})
    # read from ConfigParser object's defaults section into a dictionary.
    # config.defaults() (ConfigParser method) returns a dict of the default
    # options as specified above
    config_options = config.defaults()  # (\\label{lst:storedefault})

    # config_options is dictionary of _strings_(see above dict),
    # override respective correct # default types here
    # * you dont need to provide every possible option here, just the ones with
    # default values overriden  # (\\label{lst:override})
    config_options['magmin'] = config.getfloat('DEFAULT', 'magmin')
    config_options['dt'] = config.getfloat('DEFAULT', 'dt')
    config_options['preset'] = config.getfloat('DEFAULT', 'preset')
    config_options['offset'] = config.getfloat('DEFAULT', 'offset')
    # it's not possible to override the start and end time defaults here, since
    # they are of obspy's own UTCDateTime type. will handle below.

    # feed config_options dictionary of defaults into parser object
    parser.set_defaults(**config_options)

    # parse command line options
    (options, args) = parser.parse_args()  # (\\label{lst:optiontpl})
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
    ##########################################################################
    # VARIABLE SPLITTING AND SANITY CHECK SECTION as described in the thesis #
    ##########################################################################
    # print long help if -H  # (\\label{lst:varsplit})
    if options.showhelp:
        help()
        sys.exit()
    # Sanity check for velocity model
    if options.model != 'iasp91' and options.model != 'ak135':
        print "Erroneous velocity model given:"
        print "correct are '-v iasp91' or '-v ak135'."
        sys.exit(2)
    # parse pixel sizes and timespan of the plot if -I  # (\\label{lst:pltbeg})
    if options.plt:
        try:
            # this will do it's job if the user has given a timespan
            size, timespan = options.plt.split('/')
            if size == 'd' or size == 'default':
                pltWidth, pltHeight, colWidth = 1200, 800, 1
            else:
                try:
                    pltWidth, pltHeight, colWidth = size.split('x')
                    pltWidth = int(pltWidth)
                    pltHeight = int(pltHeight)
                    colWidth = int(colWidth)
                except:
                    print "Erroneous plot size given."
                    print "Format: e.g. -I 800x600x1/80"
                    sys.exit(0)
            try:
                timespan = float(timespan)
                # we need the timespan in seconds later
                timespan *= 60
            except:
                print "Erroneous timespan given."
                print "Format: e.g. -I d/80"
                sys.exit(0)
        except:
            # we're in here if the user did not provide a timespan
            if options.plt == 'd' or options.plt == 'default':
                pltWidth, pltHeight, colWidth = 1200, 800, 1
            else:
                try:
                    pltWidth, pltHeight, colWidth = options.plt.split('x')
                    pltWidth = int(pltWidth)
                    pltHeight = int(pltHeight)
                    colWidth = int(colWidth)
                except:
                    print "Erroneous plot size given."
                    print "Format: e.g. -I 800x600x3"
                    sys.exit(0)
            # this is the default timespan if no timespan was provided
            timespan = 100 * 60.0
        if options.debug:
            print "pltWidth: ", pltWidth
            print "pltHeight: ", pltHeight
            print "colWidth: ", colWidth
            print "timespan: ", timespan
    # parse phases into a list of strings usable with travelTimePlot
    try:
        if options.phases == 'none':
            pltPhases = []
        elif options.phases == 'all':
            pltPhases = ['P', "P'P'ab", "P'P'bc", "P'P'df", 'PKKPab', 'PKKPbc',
                    'PKKPdf', 'PKKSab', 'PKKSbc', 'PKKSdf', 'PKPab', 'PKPbc',
                    'PKPdf', 'PKPdiff', 'PKSab', 'PKSbc', 'PKSdf', 'PKiKP',
                    'PP', 'PS', 'PcP', 'PcS', 'Pdiff', 'Pn', 'PnPn', 'PnS',
                    'S', "S'S'ac", "S'S'df", 'SKKPab', 'SKKPbc', 'SKKPdf',
                    'SKKSac', 'SKKSdf', 'SKPab', 'SKPbc', 'SKPdf', 'SKSac',
                    'SKSdf', 'SKiKP', 'SP', 'SPg', 'SPn', 'SS', 'ScP', 'ScS',
                    'Sdiff', 'Sn', 'SnSn', 'pP', 'pPKPab', 'pPKPbc', 'pPKPdf',
                    'pPKPdiff', 'pPKiKP', 'pPdiff', 'pPn', 'pS', 'pSKSac',
                    'pSKSdf', 'pSdiff', 'sP', 'sPKPab', 'sPKPbc', 'sPKPdf',
                    'sPKPdiff', 'sPKiKP', 'sPb', 'sPdiff', 'sPg', 'sPn', 'sS',
                    'sSKSac', 'sSKSdf', 'sSdiff', 'sSn']
        else:
            pltPhases = options.phases.split(',')
    except:
        print "Erroneous phases given."
        print "Format: e.g. -a P,S,PKPdiff"
        sys.exit(0)  # (\\label{lst:pltend})
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
                sys.exit(2)
            options.west = float(options.rect[0])
            options.east = float(options.rect[1])
            options.south = float(options.rect[2])
            options.north = float(options.rect[3])
        except:
            print "Erroneous rectangle given."
            print optarg, rect
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
        sys.exit(2)
    if options.debug:
        print "Now it's UTCDateTime:"
        print "options.start", options.start
        print "options.end", options.end
    ################################################### (\\label{lst:spcl})
    # SPECIAL TASK SECTION as described in the thesis #
    ###################################################
    cwd = os.getcwd()
    # change default datapath if in metadata mode # (\\label{lst:metachange})
    if options.metadata and options.datapath == 'obspyload-data':
        options.datapath = os.path.join(cwd, 'obspyload-metadata')
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
    # if -q oder --query-metadata, do not enter normal data download operation,
    # but download metdata and quit. # (\\label{lst:othermodes})
    if options.metadata:
        print "ObsPyLoad will download resp and dataless seed instrument " + \
              "files and quit.\n"
        queryMeta(options.west, options.east, options.south, options.north,
                  options.start, options.end, options.nw, options.st,
                  options.lo, options.ch, options.permanent, options.debug)
        return
    # if -E oder --exceptions, do not enter normal data download operation,
    # operation, but read exceptions.txt and try to download again and quit.
    if options.exceptions:
        print "ObsPyLoad will now try to download the data that returned " + \
              "an error other than 'no data available' last time.\n"
        exceptionMode(debug=options.debug)
        return
    # if -u or --update, delete event and catalog pickled objects
    if options.update:
        try:
            os.remove(os.path.join(datapath, 'events.pickle'))
            os.remove(os.path.join(datapath, 'inventory.pickle'))
            os.remove(os.path.join(datapath, 'availability.pickle'))
        except:
            pass
    # Warn that datapath will be created and give list of further options
    # (\\label{lst:msg})
    if not options.force:
        if not os.path.isdir(datapath):
            if len(sys.argv) == 1:
                print "\nWelcome,"
                print "you provided no options, using all default values will"
                print "download every event that occurred in the last 3 months"
                print "with magnitude > 3 from every available station."
            print "\nObsPyLoad will now create the folder %s" % datapath
            print "and possibly download vast amounts of data. Continue?"
            print "Note: you can suppress this message with -f or --force"
            print "Brief help: obspyload.py -h"
            print "Long help: obspyload.py -H"
            answer = raw_input("[y/N]> ")
            if answer != "y":
                print "Exiting ObsPyLoad."
                sys.exit(2)
        else:
            print "Found existing data folder %s" % datapath
            msg = "Resume download?\nNotes:"
            msg += "- suppress this message with -f or --force\n"
            msg += "- update the event database before resuming download "
            msg += "with -u or --update\n"
            msg += "- reset and redownload everything, including all data, "
            msg += "with -R or --reset\n"
            msg += "Brief help: obspyload.py -h\n"
            msg += "Long help: obspyload.py -H"
            print msg
            answer = raw_input("[y/N]> ")
            if answer != "y":
                print "Exiting obspy."
                sys.exit(2)
    ############################################################
    # DATA DOWNLOAD ROUTINE SECTION as described in the thesis #
    ############################################################
    # create datapath # (\\label{lst:datadl})
    if not os.path.exists(datapath):
        os.mkdir(datapath)
    # start keypress thread, so we can quit by pressing 'q' anytime from now on
    # during the downloads
    done = False
    keypress_thread().start()
    # (1) get events from NERIES-eventservice # (\\label{lst:1})
    if options.debug:
        print '#############'
        print "options: ", options
        print '#############'
    events = get_events(options.west, options.east, options.south,
                            options.north, options.start, options.end,
                            options.magmin, options.magmax)
    if options.debug:
        print 'events from NERIES:', events
    # (2) get inventory data from ArcLink # (\\label{lst:2})
    # check if the user pressed 'q' while we did d/l eventlists.
    check_quit()
    arclink_stations = get_inventory(options.start, options.end, options.nw,
                              options.st, options.lo, options.ch,
                              permanent=options.permanent,
                              debug=options.debug)
    # arclink_stations is a list of tuples of all stations:
    # [(station1, lat1, lon1), (station2, lat2, lon2), ...]
    if options.debug:
        print 'arclink_stations returned from get_inventory:', arclink_stations
    # (3) Get availability data from IRIS # (\\label{lst:3})
    # check if the user pressed 'q' while we did d/l the inventory from ArcLink
    check_quit()
    avail = getnparse_availability(start=options.start, end=options.end,
                                   nw=options.nw, st=options.st, lo=options.lo,
                                   ch=options.ch, debug=options.debug)
    irisclient = obspy.iris.Client(debug=options.debug)
    # (4) create and write to catalog file # (\\label{lst:4})
    headline = "event_id;datetime;origin_id;author;flynn_region;"
    headline += "latitude;longitude;depth;magnitude;magnitude_type;"
    headline += "DataQuality;TimingQualityMin\n" + "#" * 126 + "\n\n"
    hl_eventf = "Station;Data Provider;TQ min;Gaps;Overlaps" + "\n"
    hl_eventf += "#" * 42 + "\n\n"
    catalogfp = os.path.join(datapath, 'catalog.txt')
    # open catalog file in read and write mode in case we are continuing d/l,
    # so we can append to the file
    try:
        catalogfout = open(catalogfp, 'r+t')
    except:
        # the file did not exist, we are not continuing d/l
        catalogfout = open(catalogfp, 'wt')
    catalogfout.write(headline)
    # move to end of catalog file. that way if we are continuing downloading,
    # we overwrote the headline with the same headline again and now continue
    # to write new entries to the end of the file.
    catalogfout.seek(0, 2)
    # initialize ArcLink webservice client
    arcclient = obspy.arclink.Client(timeout=5, debug=options.debug)
    mseed = LibMSEED()
    # (5) Loop through events # (\\label{lst:5})
    # create exception file
    # this file will contain any information about exceptions while trying to
    # download data: the event we were trying to d/l, starttime, endtime,
    # the station, the exception
    exceptionfp = os.path.join(datapath, 'exceptions.txt')
    # try open exceptionfile in read and write mode if we continue d/l
    try:
        exceptionfout = open(exceptionfp, 'r+t')
        # we need to know about exceptions encountered last time, so we can
        # skip them this time. if the user wants to try again to d/l
        # exceptions, he will use the -E exception mode
        # i'll just read the whole file into one string and check for each
        # station whether it's in the string
        exceptionstr = exceptionfout.read()
        if options.debug:
            print "exceptionstr: ", exceptionstr
        # go back to beginning of exceptionfout
        exceptionfout.seek(0)
    except:
        # the file did not exist, we are not continuing d/l
        exceptionfout = open(exceptionfp, 'wt')
        exceptionstr = ''
    exceptionhl = 'event_id;data provider;station;starttime;endtime;exception'
    exceptionhl += '\n' + '#' * 58 + '\n\n'
    exceptionfout.write(exceptionhl)
    # just like for the catalog file, move to end of exception file
    exceptionfout.seek(0, 2)
    if options.plt:
        alleventsmatrix = np.zeros((pltHeight, pltWidth))
        alleventsmatrix_counter = 0
    for eventdict in events:
        check_quit()
        eventid = eventdict['event_id']  # (\\label{lst:eventxtrst})
        eventtime = eventdict['datetime']
        # extract information for taup
        eventlat = float(eventdict['latitude'])
        eventlon = float(eventdict['longitude'])
        eventdepth = float(eventdict['depth'])
        if options.debug:
            print '#############'
            print 'event:', eventid
            for key in eventdict:
                print key, eventdict[key]  # (\\label{lst:eventxtrend})
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
        # re-init neriesclient here, seems to reduce problems
        neriesclient = obspy.neries.Client()
        # download quake ml xml
        quakemlfp = os.path.join(eventdir, 'quakeml.xml')
        if not os.path.isfile(quakemlfp):
            print "Downloading quakeml xml file for event %s..." % eventid,
            try:
                quakeml = neriesclient.getEventDetail(eventid, 'xml')
                quakemlfout = open(quakemlfp, 'wt')  # (\\label{lst:quakeml})
                quakemlfout.write(quakeml)
                quakemlfout.close()
            except Exception, error:
                print "error:", error
            else:
                print "done."
        else:
            print "Found existing quakeml xml file for event %s, skip..." \
                                                                      % eventid
        # init/reset dqsum  # (\\label{lst:initsum})
        dqsum = 0
        tqlist = []
        # create event file in event dir
        # DQ: all min entries in event folder txt file differently
        # this is handled inside the station loop
        quakefp = os.path.join(eventdir, 'quake.txt')
        # open quake file in read and write mode in case we are continuing d/l,
        # so we can append to the file
        try:
            quakefout = open(quakefp, 'r+t')
        except:
            # the file did not exist, we are not continuing d/l
            quakefout = open(quakefp, 'wt')
        quakefout.write(headline[:97] + "\n" + "#" * 97 + "\n\n")
        quakefout.write(infoline + '\n\n\n')
        quakefout.write(hl_eventf)
        quakefout.flush()
        # just like for catalog and exception file, move to end of quake file
        # to write new stations to the end of it
        quakefout.seek(0, 2)
        # init matrix containing all station plots - will be used to plot
        # all station waveforms later. +1 because the [0] entry of each col
        # works as a counter
        if options.plt:
            stmatrix = np.zeros((pltHeight + 1, pltWidth))  # (\\label{lst:st})
        # (5.1) ArcLink wf data download loop (runs inside event loop)
        # Loop trough arclink_stations  # (\\label{lst:5.1})
        for station in arclink_stations:
            check_quit()
            # station is a tuple of (stationname, lat, lon)
            try:
                stationlat = station[1]
                stationlon = station[2]
                station = station[0]
            except:
                continue
            if options.debug:
                print "station: ", station
            # skip dead networks
            net, sta, loc, cha = station.split('.')
            if net in skip_networks:
                print 'Skipping dead network %s...' % net
                # continue the for-loop to the next iteration
                continue
            # create data file pointer  # (\\label{lst:datafp})
            datafout = os.path.join(eventdir, "%s.mseed" % station)
            if os.path.isfile(datafout):
                print 'Data file for event %s from %s exists, skip...' \
                                                           % (eventid, station)
                continue
            # if this string has already been in the exception file when we
            # were starting the d/l, we had an exception for this event/data
            # provider/station combination last time and won't try again.
            skipstr = eventid + ';ArcLink;' + station  # (\\label{lst:skipstr})
            if skipstr in exceptionstr:
                msg = 'Encountered exception for event %s from ArcLink %s last'
                msg += ' time, skip...'
                print msg % (eventid, station)
                continue  # (\\label{lst:skipend})
            # use taup to calculate the correct starttime and endtime for
            # waveform retrieval at this station
            distance = taup.locations2degrees(eventlat, eventlon, stationlat,
                                              stationlon)
            if options.debug:
                print "distance :", distance, type(distance)
                print "eventdepth: ", eventdepth, type(eventdepth)
                print "options.model: ", options.model
            traveltimes = taup.getTravelTimes(distance, eventdepth,
                                              model=options.model)
            if options.debug:
                print "traveltimes: ", traveltimes
            # find the earliest arrival time
            arrivaltime = 99999
            for phase in traveltimes:
                if phase['time'] < arrivaltime:
                    arrivaltime = phase['time']  # (\\label{lst:arrival})
            if options.debug:
                print "earliest arrival time: ", arrivaltime
            starttime = eventtime + arrivaltime - options.preset
            endtime = eventtime + arrivaltime + options.offset
            print 'Downloading event %s from ArcLink %s...' \
                                                          % (eventid, station),
            try:
                # I have been told that often initializing the client reduces
                # problems
                arcclient = obspy.arclink.Client(timeout=5,
                                                 debug=options.debug)
                # catch exception so the d/l continues if only one doesn't work
                arcclient.saveWaveform(filename=datafout, network=net,
                                       station=sta, location=loc, channel=cha,
                                       starttime=starttime, endtime=endtime)
            except Exception, error:
                print "download error: ",
                print error
                # create exception file info line
                il_exception = str(eventid) + ';ArcLink;' + station + ';'
                il_exception += str(starttime) + ';' + str(endtime) + ';'
                il_exception += str(error) + '\n'
                exceptionfout.write(il_exception)
                exceptionfout.flush()
                continue
            else:
                # else code will run if try returned no exception!
                # write station name to event info line  # (\\label{lst:qcbeg})
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
                il_quake += ';%d;%d\n' % (gaps, overlaps)
                quakefout.write(il_quake)
                quakefout.flush()  # (\\label{lst:qcend})
                # if there has been no Exception, assume d/l was ok
                print "done."
                if options.plt:
                    # referencing st[0] with tr  # (\\label{lst:pltbeg})
                    tr = st[0]
                    if options.fill:
                        # if the user gave -F option  # (\\label{lst:fillbeg})
                        print "Getting and scaling data for station plot...",
                        del st
                        # get data for the whole timeframe needed for the
                        # plot. We don't want to save this, it's just needed
                        # for the (rectangular) plot
                        try:
                            st = arcclient.getWaveform(network=net,
                                              station=sta, location=loc,
                                              channel=cha, starttime=eventtime,
                                              endtime=eventtime + timespan)
                        except Exception, error:
                            print "error: ",
                            print error
                            continue  # (\\label{lst:fillend})
                        # the way we downloaded data, there should always be
                        # exactly one trace in each stream object
                    else:
                        # if the user did not provide -F, we wont d/l any more
                        # data. we need trim existing data:
                        print "Scaling data for station plot...",
                        tr.trim(starttime=eventtime,
                                endtime=eventtime + timespan, pad=True,
                                fill_value=0)
                    # x axis / abscissa - distance
                    # y axis / ordinate - time
                    # normalize the trace, needed for plotting
                    tr.normalize()  # (\\label{lst:trnorm})
                    # obtain the time increment that passes between samples
                    # delta = tr.stats['delta']
                    # scale down the trace array so it matches the output size
                    # using scipy since that's faster than letting the plotting
                    # function handle it
                    pixelcol = np.around(scipy.ndimage.interpolation.zoom(
                                                  tr,
                                                  float(pltHeight) / len(tr)),
                                         7)
                    if options.debug:
                        print "pixelcol: ", pixelcol
                    # Find the pixel column that represents the distance of
                    # this station. if the colWidth is >1, we need to plot the
                    # station to the according width, reducing the internal
                    # resolution of the plot by this factor
                    x_coord = int((distance / 180.0) * pltWidth)
                    # now we need to floor down to the next multiple of the
                    # station column width:
                    x_coord -= x_coord % colWidth  # (\\label{lst:floor})
                    # Add trace as one column to waveform matrix. the [0] entry
                    # of the matrix counts how many waveforms have been added
                    # to that column (this will be normalized later)
                    # For no (to me) apparent reason, sometimes
                    # scipy.ndimage.interpolation.zoom returns a slightly
                    # different array size, so I use try-except.
                    # It seems to be worse with some output sizes and no
                    # problem at all with other ones.
                    if options.debug:
                        print "len stack: ", len(np.hstack((1, abs(pixelcol))))
                        print "len stmatrixslice: ", len(stmatrix[:, x_coord])
                    # add counter entry to pixelcol and take absolute of all
                    # values in pixelcol
                    pixelcol = np.hstack((1, abs(pixelcol)))
                    try:
                        # add pixelcol to 1 or more columns, depending on the
                        # chosen width of the station columns  # (\\label{stm})
                        stmatrix[:, x_coord:x_coord + colWidth] += \
                                   np.vstack([pixelcol] * colWidth).transpose()
                    except:
                        print "failed."
                        continue
                    if options.debug:
                        print "stmatrix: ", stmatrix
                    print "done."  # (\\label{lst:trnormend})
                del st
        # (5.2) Iris wf data download loop  # (\\label{lst:5.2})
        for net, sta, loc, cha, stationlat, stationlon in avail:
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
            # if this string has already been in the exception file when we
            # were starting the d/l, we had an exception for this event/data
            # provider/station combination last time and won't try again.
            skipstr = eventid + ';IRIS;' + station
            if skipstr in exceptionstr:
                msg = 'Encountered exception for event %s from IRIS %s last '
                msg += 'time, skip...'
                print msg % (eventid, station)
                continue
            print 'Downloading event %s from IRIS %s...' % (eventid, station),
            # use taup to calculate the correct starttime and endtime for
            # waveform retrieval at this station
            distance = taup.locations2degrees(eventlat, eventlon, stationlat,
                                              stationlon)
            traveltimes = taup.getTravelTimes(distance, eventdepth,
                                              model=options.model)
            # find the earliest arrival time
            arrivaltime = 99999
            for phase in traveltimes:
                if phase['time'] < arrivaltime:
                    arrivaltime = phase['time']
            if options.debug:
                print "earliest arrival time: ", arrivaltime
            starttime = eventtime + arrivaltime - options.preset
            endtime = eventtime + arrivaltime + options.offset
            try:
                # I have been told that initializing the client often reduces
                # problems
                irisclient = obspy.iris.Client(debug=options.debug)
                irisclient.saveWaveform(filename=irisfnfull,
                                        network=net, station=sta,
                                        location=loc, channel=cha,
                                        starttime=starttime, endtime=endtime)
            except Exception, error:
                print "download error: ", error
                # create exception file info line
                il_exception = str(eventid) + ';IRIS;' + station + ';'
                il_exception += str(starttime) + ';' + str(endtime) + ';'
                il_exception += str(error) + '\n'
                exceptionfout.write(il_exception)
                exceptionfout.flush()
                continue
            else:
                # if there was no exception, the d/l should have worked
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
                print "done."
                if options.plt:
                    # this is the same as for arclink, I did not want to
                    # replicate the comments, see above for them
                    tr = st[0]
                    if options.fill:
                        print "Getting and scaling data for station plot...",
                        del st
                        try:
                            st = irisclient.getWaveform(network=net,
                                              station=sta, location=loc,
                                              channel=cha, starttime=eventtime,
                                              endtime=eventtime + timespan)
                        except Exception, error:
                            print "error: ",
                            print error
                            continue
                    else:
                    # if the user did not provide -F, fill up existing data:
                        print "Scaling data for station plot...",
                        tr.trim(starttime=eventtime,
                                endtime=eventtime + timespan, pad=True,
                                fill_value=0)
                    tr.normalize()
                    pixelcol = np.around(scipy.ndimage.interpolation.zoom(
                                                  tr,
                                                  float(pltHeight) / len(tr)),
                                         7)
                    if options.debug:
                        print "pixelcol: ", pixelcol
                    x_coord = int((distance / 180.0) * pltWidth)
                    x_coord -= x_coord % colWidth
                    if options.debug:
                        print "len stack: ", len(np.hstack((1, abs(pixelcol))))
                        print "len stmatrixslice: ", len(stmatrix[:, x_coord])
                    pixelcol = np.hstack((1, abs(pixelcol)))
                    try:
                        stmatrix[:, x_coord:x_coord + colWidth] += \
                                   np.vstack([pixelcol] * colWidth).transpose()
                    except:
                        print "failed."
                        continue
                    if options.debug:
                        print "stmatrix: ", stmatrix
                    print "done."
                del st
                il_quake += ';%d;%d\n' % (gaps, overlaps)
                quakefout.write(il_quake)
                quakefout.flush()
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
        ### end of station loop ###
        # close quake file
        quakefout.close()
        if options.plt:
            # normalize each distance column - the [0, i] entry has been
            # counting how many stations we did add at that distance
            for i in range(pltWidth - 1):
                if stmatrix[0, i] != 0:
                    stmatrix[:, i] /= stmatrix[0, i]
            # [1:,:] because we do not want to display the counter
            plt.imshow(stmatrix[1:, :], vmin=0.001, vmax=1,
                       origin='lower', cmap=plt.cm.hot_r,
                       norm=mpl.colors.LogNorm(vmin=0.001, vmax=1))
            plt.xticks(range(0, pltWidth, pltWidth / 4),
                             ('0', '45', '90', '135', '180'), rotation=45)
            y_incr = timespan / 60 / 4
            plt.yticks(range(0, pltHeight, pltHeight / 4),
                      ('0', str(y_incr), str(2 * y_incr), str(3 * y_incr),
                       str(3 * y_incr)))
            plt.xlabel('Distance from epicenter in degrees')
            plt.ylabel('Time after origin time in minutes')
            titlemsg = "Event %s:\ndata and " % eventid + \
                       "theoretical arrival times\n"
            plt.title(titlemsg)
            cbar = plt.colorbar()
            mpl.colorbar.ColorbarBase.set_label(cbar, 'Relative amplitude')
            # add taupe theoretical arrival times points to plot
            # invoking travelTimePlot function, taken and fitted to my needs
            # from the obspy.taup package
            # choose npoints value depending on plot size, but not for every
            # pixel so pdf conversion won't convert the points to a line
            travelTimePlot(npoints=pltWidth / 10, phases=pltPhases,
                           depth=eventdepth, model=options.model,
                           pltWidth=pltWidth, pltHeight=pltHeight,
                           timespan=timespan)
            # construct filename and save event plots
            print "Done with event %s, saving plots..." % eventid
            if options.debug:
                print "stmatrix: ", stmatrix
            plotfn = os.path.join(datapath, eventid, 'waveforms.pdf')
            plt.savefig(plotfn)
            # clear figure
            plt.clf()
            alleventsmatrix += stmatrix[1:, :]
            alleventsmatrix_counter += 1
            del stmatrix
    # save plot of all events, similar as above, for comments see above
    if options.plt:
        print "Saving plot of all events stacked..."
        plt.imshow(alleventsmatrix / alleventsmatrix_counter,
                   origin='lower', cmap=plt.cm.hot_r,
                   norm=mpl.colors.LogNorm(vmin=0.01, vmax=1))
        plt.xticks(range(0, pltWidth, pltWidth / 4),
                         ('0', '45', '90', '135', '180'), rotation=45)
        y_incr = timespan / 60 / 4
        plt.yticks(range(0, pltHeight, pltHeight / 4),
                  ('0', str(y_incr), str(2 * y_incr), str(3 * y_incr),
                   str(3 * y_incr)))
        plt.xlabel('Distance from epicenter in degrees')
        plt.ylabel('Time after origin time in minutes')
        titlemsg = "%s events data stacked\n" % len(events)
        plt.title(titlemsg)
        cbar = plt.colorbar()
        mpl.colorbar.ColorbarBase.set_label(cbar, 'Relative amplitude')
        travelTimePlot(npoints=pltWidth / 10, phases=pltPhases,
                       depth=10, model=options.model,
                       pltWidth=pltWidth, pltHeight=pltHeight,
                       timespan=timespan)
        plotfn = os.path.join(datapath, 'allevents_waveforms.pdf')
        plt.savefig(plotfn)
    # done with ArcLink, remove ArcLink client
    del arcclient
    # done with iris, remove client
    del irisclient
    ### end of event loop ###
    # close event catalog info file and exception file
    catalogfout.close()
    exceptionfout.close()
    done = True
    return

# (\\label{lst:dataser})
#############################################################
# DATA SERVICE FUNCTIONS SECTION as described in the thesis #
#############################################################


def get_events(west, east, south, north, start, end, magmin, magmax):
    """
    Downloads and saves a list of events if not present in datapath.

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
        result = pickle.load(fh)
        fh.close()
        print "Found eventlist in datapath, skip download."
    except:
        print "Downloading NERIES eventlist...",
        client = obspy.neries.Client()
        # the maximum no of allowed results seems to be not allowed to be too
        # large, but 9999 seems to work, 99999 results in a timeout error in
        # urllib. implemented the while-loop to work around this restriction:
        # query is repeated until we receive less than 9999 results.
        result = []
        events = range(9999)  # (\\label{lst:getevents})
        while len(events) == 9999:
            events = client.getEvents(min_latitude=south, max_latitude=north,
                                  min_longitude=west, max_longitude=east,
                                  min_datetime=start, max_datetime=end,
                                  min_magnitude=magmin, max_magnitude=magmax,
                                  max_results=9999)
            result.extend(events)
            try:
                start = events[-1]['datetime']
            except:
                pass
        del client
        # dump events to file
        fh = open(eventfp, 'wb')
        pickle.dump(result, fh)
        fh.close()
        print "done."
    print("Received %d event(s) from NERIES." % (len(result)))
    return result


def get_inventory(start, end, nw, st, lo, ch, permanent, debug=False):
    """
    Searches the ArcLink inventory for available networks and stations.
    Because the ArcLink webservice does not support wildcard searches for
    networks (but for everything else), this method uses the re module to
    find * and ? wildcards in ArcLink networks and returns only matching
    network/station combinations.

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
        A list of tuples of the form [(station1, lat1, lon1), ...]
    """
    # create data path:
    if not os.path.isdir(datapath):
        os.mkdir(datapath)
    inventoryfp = os.path.join(datapath, 'inventory.pickle')
    try:
        # first check if inventory data has already been downloaded
        fh = open(inventoryfp, 'rb')
        stations3 = pickle.load(fh)
        fh.close()
        print "Found inventory data in datapath, skip download."
        return stations3
    except:
        # first take care of network wildcard searches as arclink does not
        # support anything but '*' here:
        nwcheck = False
        if '*' in nw and nw != '*' or '?' in nw:
            if debug:
                print "we're now setting nwcheck = True"
            nw2 = '*'
            nwcheck = True  # (\\label{lst:nwcheck})
        else:
            nw2 = nw
        arcclient = obspy.arclink.client.Client()
        print "Downloading ArcLink inventory data...",
        # restricted = false, we don't want restricted data
        # permanent is handled via command line flag
        if debug:
            print "permanent flag: ", permanent
        try:
            inventory = arcclient.getInventory(network=nw2, station=st,
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
            print "done."
    stations = sorted([i for i in inventory.keys() if i.count('.') == 3])
    if debug:
        print "inventory inside get_inventory(): ", inventory
        print "stations inside get_inventory(): ", stations
    # stations is a list of 'nw.st.lo.ch' strings and is what we want
    # check if we need to search for wildcards:  # (\\label{lst:ifnwchck})
    if nwcheck:
        stations2 = []
        # convert nw (which is 'b?a*' type string, using normal wildcards into
        # equivalent regular expression
        # using fnmatch.translate to translate ordinary wildcard into regex.
        nw = fnmatch.translate(nw)
        if debug:
            print "regex nw: ", nw
        p = re.compile(nw, re.IGNORECASE)
        for i in range(len(stations)):
            # split every station('nw.st.lo.ch') by the . and take the first
            # object which is 'nw', search for the regular expression inside
            # this network string. if it matches, the if condition will be met
            # (p.match returns None if nothing is found)
            if p.match(stations[i].split('.')[0]):
                # everything is fine, we can return this station
                stations2.append(stations[i])
    else:
        # just return the whole stations list otherwise
        stations2 = stations
    # include latitude and longitude for taup in the dict stations3, which will
    # be a list of tuples (station, lat, lon)
    stations3 = []
    for station in stations2:
        # obtain key for station Attrib dict
        net, sta, loc, cha = station.split('.')
        key = '.'.join((net, sta))
        stations3.append((station, inventory[key]['latitude'],
                                  inventory[key]['longitude']))
    print("Received %d channel(s) from ArcLink." % (len(stations3)))
    if debug:
        print "stations2 inside get_inventory: ", stations2
        print "stations3 inside get_inventory: ", stations3
    # dump result to file so we can quickly resume d/l if obspyload
    # runs in the same dir more than once. we're only dumping stations (the
    # regex matched ones, since only those are needed. see the try statement
    # above, if this file is found later, we don't have to perform the regex
    # search again.
    fh = open(inventoryfp, 'wb')
    pickle.dump(stations3, fh)
    fh.close()
    return stations3


def getnparse_availability(start, end, nw, st, lo, ch, debug):
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
        fh = open(availfp, 'rb')  # (\\label{lst:availopen})
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
                                     endtime=UTCDateTime(end), output='xml')
        except Exception, error:
            print "\nIRIS returned no matching stations."
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
            stations = availxml.findall('Station')
            # I will construct a list of tuples of stations of the form:
            # [(net,sta,cha,loc,lat,lon), (net,sta,loc,cha,lat,lon), ...]
            avail_list = []  # (\\label{lst:lpbeg})
            for station in stations:
                net = station.values()[0]
                sta = station.values()[1]
                # find latitude and longitude of station
                lat = float(station.find('Lat').text)
                lon = float(station.find('Lon').text)
                channels = station.findall('Channel')
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
                                       loc.strip(' '), cha.strip(' '), lat,
                                       lon))  # (\\label{lst:lpend})
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
# (\\label{lst:altermodes})
##################################################################
# ALTERNATIVE MODES FUNCTIONS SECTION as described in the thesis #
##################################################################


def queryMeta(west, east, south, north, start, end, nw, st, lo, ch, permanent,
              debug):
    """
    Downloads Resp instrument data and dataless seed files.
    """
    global quit, done, skip_networks
    # start keypress thread, so we can quit by pressing 'q' anytime from now on
    # during the downloads
    done = False
    keypress_thread().start()
    irisclient = obspy.iris.Client(debug=debug)
    arclinkclient = obspy.arclink.client.Client(debug=debug)
    # (0) get availability and inventory first
    # get and parse IRIS availability xml
    avail = getnparse_availability(start=start, end=end, nw=nw, st=st, lo=lo,
                                   ch=ch, debug=debug)
    # get ArcLink inventory
    stations = get_inventory(start, end, nw, st, lo, ch, permanent=permanent,
                             debug=debug)
    # (1) IRIS: resp files
    # stations is a list of all stations (nw.st.l.ch, so it includes networks)
    # loop over all tuples of a station in avail list:  # (\\label{lst:availp})
    for (net, sta, loc, cha, lat, lon) in avail:
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
            # initializing the client each time should reduce problems
            irisclient = obspy.iris.Client(debug=debug)
            irisclient.saveResponse(respfnfull, net, sta, loc, cha, start, end,
                                    format='RESP')  # (\\label{lst:saveresp})
        except Exception, error:
            print "\ndownload error: ",
            print error
            continue
        else:
            # if there has been no exception, the d/l should have worked
            print 'done.'
    # (2) ArcLink: dataless seed
    # loop over stations to d/l every dataless seed file...
    # skip dead ArcLink networks  # (\\label{lst:arclpbeg})
    for station in stations:
        check_quit()
        # we don't need lat and lon
        station = station[0]
        net, sta, loc, cha = station.split('.')
        # skip dead networks
        if net in skip_networks:
            print 'Skipping dead network %s...' % net
            # continue the for-loop to the next iteration
            continue
        # construct filename
        dlseedfn = '.'.join((net, sta, loc, cha)) + '.seed'
        dlseedfnfull = os.path.join(datapath, dlseedfn)
        # create data file handler
        dlseedfnfull = os.path.join(datapath, "%s.mseed" % station)
        if os.path.isfile(dlseedfnfull):
            print 'Dataless file for %s exists, skip download...' % dlseedfn
            continue
        print 'Downloading dataless seed file for %s from ArcLink...' \
                                                                  % dlseedfn,
        try:
            # catch exception so the d/l continues if only one doesn't work
            # again, initializing the client should reduce problems
            arclinkclient = obspy.arclink.client.Client(debug=debug)
            arclinkclient.saveResponse(dlseedfnfull, net, sta, loc, cha,
                                       start, end, format='SEED')
        except Exception, error:
            print "download error: ",
            print error
            continue
        else:
            # if there has been no exception, the d/l should have worked
            print 'done.'  # (\\label{lst:arclpend})
    done = True
    return


def exceptionMode(debug):
    """
    This will read the file 'exceptions.txt' and try to download all the data
    that returned an exception other than 'no data available' last time.
    """
    # initialize both clients, needed inside every loop.
    arcclient = obspy.arclink.Client(timeout=5, debug=debug)
    irisclient = obspy.iris.Client(debug=debug)
    # read exception file
    exceptionfp = os.path.join(datapath, 'exceptions.txt')
    exceptionfin = open(exceptionfp, 'rt')
    exceptions = exceptionfin.readlines()
    exceptionfin.close()
    # create further_exceptions string, this will be used to overwrite the
    # exceptionfile, but only after the process if done so we won't loose our
    # original exceptions (exception file) if the user presses q while d/l
    further_exceptions = exceptions[0] + exceptions[1] + exceptions[2]
    if debug:
        print "further_exceptions: ", further_exceptions
    for exception in exceptions[3:]:
        check_quit()
        if debug:
            print "exception: ", exception
        exsplit = exception.split(';')
        if debug:
            print "exsplit: ", exsplit  # (\\label{lst:nodatabeg})
        if not "data available" in exsplit[5]:
            # we want to d/l this one again
            if debug:
                print "passed no data available test."
            eventid = exsplit[0]
            station = exsplit[2]
            net, sta, loc, cha = station.split('.')
            starttime = UTCDateTime(exsplit[3])
            endtime = UTCDateTime(exsplit[4])
            datafout = os.path.join(datapath, eventid, station + '.mseed')
            if debug:
                print "datafout: ", datafout
            # check if ArcLink or IRIS
            if exsplit[1] == "ArcLink":
                print "Trying to download event %s from ArcLink %s..." % \
                                                           (eventid, station),
                try:
                    arcclient = obspy.arclink.Client(timeout=5, debug=debug)
                    arcclient.saveWaveform(filename=datafout, network=net,
                                       station=sta, location=loc, channel=cha,
                                       starttime=starttime, endtime=endtime)
                except Exception, error:
                    print "download error: ",
                    print error
                    # create exception info line
                    il_exception = str(eventid) + ';ArcLink;' + station + ';'
                    il_exception += str(starttime) + ';' + str(endtime) + ';'
                    il_exception += str(error) + '\n'
                    further_exceptions += il_exception
                    continue
                else:
                    print "done."
            elif exsplit[1] == "IRIS":
                print "Trying to download event %s from IRIS %s..." % \
                                                           (eventid, station),
                try:
                    irisclient = obspy.iris.Client(debug=debug)
                    irisclient.saveWaveform(filename=datafout,
                                            network=net, station=sta,
                                            location=loc, channel=cha,
                                          starttime=starttime, endtime=endtime)
                except Exception, error:
                    print "download error: ", error
                    # create exception file info line
                    il_exception = str(eventid) + ';IRIS;' + station + ';'
                    il_exception += str(starttime) + ';' + str(endtime) + ';'
                    il_exception += str(error) + '\n'
                    further_exceptions += il_exception
                    continue
                else:
                    print "done."  # (\\label{lst:nodataend})
    exceptionfout = open(exceptionfp, 'wt')
    exceptionfout.write(further_exceptions)  # (\\label{lst:further})
    exceptionfout.close()
    done = True
    return
# (\\label{lst:addfct})
###########################################################
# ADDITIONAL FUNCTIONS SECTION as described in the thesis #
###########################################################


def travelTimePlot(npoints, phases, depth, model, pltWidth, pltHeight,
                   timespan):
    """
    Plots taupe arrival times on top of event data. This is just a modified
    version of taupe.travelTimePlot()

    :param npoints: int, optional
        Number of points to plot.
    :param phases: list of strings, optional
        List of phase names which should be used within the plot. Defaults to
        all phases if not explicit set.
    :param depth: float, optional
        Depth in kilometer. Defaults to 100.
    :param model: string
    """

    data = {}
    for phase in phases:
        data[phase] = [[], []]
    degrees = np.linspace(0, 180, npoints)  # (\\label{lst:deg})
    # Loop over all degrees.
    for degree in degrees:
        tt = taup.getTravelTimes(degree, depth, model)
        # Mirror if necessary.
        if degree > 180:
            degree = 180 - (degree - 180)
        for item in tt:
            phase = item['phase_name']
            if phase in data:
                try:
                    data[phase][1].append(item['time'])
                    data[phase][0].append(degree)
                except:
                    data[phase][1].append(np.NaN)
                    data[phase][0].append(degree)
    # Plot and some formatting.
    for key, value in data.iteritems():
        # value[0] stores all degrees, value[1] all times as lists
        # convert those values to the respective obspyload stmatrix indices:
        # divide every entry of value[0] list by 180 and sort of "multiply with
        # pltWidth" to get correct stmatrix index  # (\\label{lst:coordbeg})
        x_coord = map(operator.div, value[0], [180.0 / pltWidth] *
                  len(value[0]))
        # for the y coord, divide every entry by the timespan and mulitply with
        # pltHeight
        y_coord = map(operator.div, value[1], [timespan / pltHeight] *
                  len(value[1]))  # (\\label{lst:coordend})
        # plot arrival times on top of data
        plt.plot(x_coord, y_coord, ',', label=key)
    plt.legend()


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
    print "\nObsPyLoad: ObsPy Seismic Data Download tool."
    print "============================================\n\n"
    print "The CLI allows for different flavors of usage, in short:"
    print "--------------------------------------------------------\n"
    printWrap("e.g.:", "obspyload.py -r <west>/<east>/<south>/<north> -t " + \
          "<start>/<end> -m <min_mag> -M <max_mag> -i <nw>.<st>.<l>.<ch>")
    printWrap("e.g.:", "obspyload.py -y <min_lon> -Y <max_lon> " + \
          "-x <min_lat> -X <max_lat> -s <start> -e <end> -P <datapath> " + \
          "-o <offset> --reset -f")

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
    print "\n\n* specify plotting options:\n"
    printWrap("Default:", "no plot. If the plot will be created with -I d " + \
              "(or -I default), the defaults are 1200x800x1/100 and the " + \
              "default phases to plot are 'P' and 'S'.")
    print
    printWrap("-I[--plot]", "<pxHeight>x<pxWidth>x<colWidth>[/<timespan>]")
    printWrap("", "For each event, create one plot with the data from all " + \
                "stations together with theoretical arrival times. You " + \
                "may provide the internal plotting resolution: e.g. -I " + \
                "900x600x5. This gives you a resolution of 900x600, and " + \
                "5 units broad station columns. If -I d, or -I default, " + \
                "the default of 1200x800x1 will be used. If this " + \
                "command line parameter is not passed to ObsPyLoad at " + \
                "all, no plots will be created. You may additionally " + \
                "specify the timespan of the plot after event origin " + \
                "time in minutes: e.g. for timespan lasting 30 minutes: " + \
                "-I 1200x800x1/30 (or -I d/30). The default timespan is " + \
                "100 minutes. The final output file will be in pdf " + \
                "format.")
    print
    printWrap("-F[--fill-plot]", "")
    printWrap("", "When creating the plot, download all the data needed " + \
              "to fill the rectangular area of the plot. Note: " + \
              "depending on your options, this will approximately " + \
              "double the data download volume (but you'll end up " + \
              "with nicer plots ;-)).")
    print
    printWrap("-a[--phases]", "<phase1>,<phase2>,...")
    printWrap("", "Specify phases for which the theoretical arrival times " + \
              "should be plotted on top if creating the data plot(see " + \
              "above, -I option). " + \
              "Default: -a P,S. To plot all available phases, use -a all. " + \
              "If you just want to plot the data and no phases, use -a " + \
              "none.")
    printWrap("", "Available phases:")
    printWrap("", "P, P'P'ab, P'P'bc, P'P'df, PKKPab, PKKPbc, " + \
              "PKKPdf, PKKSab, PKKSbc, PKKSdf, PKPab, PKPbc, " + \
              "PKPdf, PKPdiff, PKSab, PKSbc, PKSdf, PKiKP, " + \
              "PP, PS, PcP, PcS, Pdiff, Pn, PnPn, PnS, " + \
              "S, S'S'ac, S'S'df, SKKPab, SKKPbc, SKKPdf, " + \
              "SKKSac, SKKSdf, SKPab, SKPbc, SKPdf, SKSac, " + \
              "SKSdf, SKiKP, SP, SPg, SPn, SS, ScP, ScS, " + \
              "Sdiff, Sn, SnSn, pP, pPKPab, pPKPbc, pPKPdf, " + \
              "pPKPdiff, pPKiKP, pPdiff, pPn, pS, pSKSac, " + \
              "pSKSdf, pSdiff, sP, sPKPab, sPKPbc, sPKPdf, " + \
              "sPKPdiff, sPKiKP, sPb, sPdiff, sPg, sPn, sS, " + \
              "sSKSac, sSKSdf, sSdiff, sSn")
    printWrap("", "Note: if you select phases with ticks(') in the " + \
              "phase name, don't forget to use quotes " + \
              "(-a \"phase1',phase2\") to avoid unintended behaviour.")
    print "\n\n* specify additional options:\n"
    printWrap("-n[--no-temporary]", "")
    printWrap("", "Instead of downloading both temporary and permanent " + \
          "networks (default), download only permanent ones.")
    print
    printWrap("-p[--preset]", "<preset>")
    printWrap("", "Time parameter given in seconds which determines how " + \
        "close the data will be cropped before estimated arrival time at " + \
        "each individual station. Default: 5 minutes.")
    print
    printWrap("-o[--offset]", "<offset>")
    printWrap("", "Time parameter given in seconds which determines how " + \
        "close the data will be cropped after estimated arrival time at " + \
        "each individual station. Default: 80 minutes.")
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
              "ObsPyLoad.")
    print
    printWrap("-u[--update]", "")
    printWrap("", "Update the event database if ObsPyLoad runs on the " + \
              "same directory for a second time.")
    print
    printWrap("-f[--force]", "")
    printWrap("", "Skip working directory warning (auto-confirm folder" + \
              " creation).")
    print "\nType obspyload.py -h for a list of all long and short options."
    print "\n\nExamples:"
    print "---------\n"
    printWrap("Alps region, minimum magnitude of 4.2:",
              "obspyload.py -r 5/16.5/45.75/48 -t 2007-01-13T08:24:00/" + \
              "2011-02-25T22:41:00 -m 4.2")
    print
    printWrap("Sumatra region, Christmas 2004, different timestring, " + \
              "mind the quotation marks:",
              "obspyload.py -r 90/108/-7/7 -t \"2004-12-24 01:23:45/" + \
              "2004-12-26 12:34:56\" -m 9")
    print
    printWrap("Mount Hochstaufen area(Ger/Aus), default minimum magnitude:",
              "obspyload.py -r 12.8/12.9/47.72/47.77 -t 2001-01-01/2011-02-28")
    print
    printWrap("Only one station, to quickly try out the plot:",
             "obspyload.py -s 2011-03-01 -m 9 -I 400x300x3 -f " + \
             "-i IU.YSS.*.*")
    print
    printWrap("ArcLink Network wildcard search:", "obspyload.py -N B? -S " + \
              "FURT -f")
    print
    printWrap("Downloading metadata from all available stations " + \
             "to folder \"metacatalog\":", "obspyload.py -q -f -P metacatalog")
    print
    printWrap("Download stations that failed last time " + \
              "(not necessary to re-enter the event/station restrictions):",
              "obspyload.py -E -P thisOrderHadExceptions -f")
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
            msg = "ObsPyLoad will finish downloading and saving the last " + \
                  "file and quit gracefully."
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
