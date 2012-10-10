#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------
#   Filename:  obspyDMT.py
#   Author:    Kasra Hosseini, Chris Scheingraber
#   Email:     hosseini@geophysik.uni-muenchen.de
#
#   Copyright (C) 2012 Kasra Hosseini
#-------------------------------------------------------------------

#for debugging: import ipdb; ipdb.set_trace()

"""
ObsPyDMT (ObsPy Data Management Tool)

Goal: Automatic tool for Downloading, Processing and Management of 
      Large Seismic Datasets

:copyright:
    The ObsPy Development Team (devs@obspy.org)
    Developed by Kasra Hosseini
:license:
    GNU General Public License, Version 3
    (http://www.gnu.org/licenses/gpl-3.0-standalone.html)
"""

#-----------------------------------------------------------------------
#----------------Import required Modules (Python and Obspy)-------------
#-----------------------------------------------------------------------

# Required Python and Obspy modules will be imported in this part.

# Added this line for python 2.5 compatibility
from __future__ import with_statement
import sys
import os
import math as math
import operator
import fnmatch
import time
import shutil
import pickle
import glob
import ConfigParser
import commands
import tarfile
from datetime import datetime
from lxml import objectify
from optparse import OptionParser

import numpy as np
import scipy
import matplotlib.pyplot as plt


try:
    from mpl_toolkits.basemap import Basemap
except Exception, error:
    bold = "\033[1m"
    reset = "\033[0;0m"
    print "******************************************************"
    print bold + "Warning:" + reset
    print "Missing dependencies (Basemap), no plotting available."
    print "For documentation please refer to:"
    print "http://matplotlib.github.com/basemap/"
    print "******************************************************"


from obspy.core import read, UTCDateTime
from obspy.signal import seisSim, invsim
from obspy.xseed import Parser
from obspy.imaging.beachball import Beach, Beachball

try:
    from obspy.core.util import locations2degrees
except Exception, error:
    bold = "\033[1m"
    reset = "\033[0;0m"
    from obspy.taup.taup import locations2degrees
    print "******************************************************"
    print bold + "Warning:" + reset
    print "locations2degrees module is imported from obspy.taup.taup"
    print "The obspy version in this machine should be updated!"
    print "******************************************************"


"""
Required Clients from Obspy will be imported here.
"""
from obspy.neries import Client as Client_neries
from obspy.iris import Client as Client_iris
from obspy.arclink import Client as Client_arclink


"""
- obspyDMT

- Parsing command-line options
- Read INPUT file (Parameters)
- Parallel Requests

- Getting List of Events/Continuous requests
- Generate desired INPUT-Periods file

- IRIS
- ArcLink

- IRIS-Updating
- ArcLink-Updating

- IRIS-instrument
- Arclink-instrument

- IRIS-merge
- ArcLink-merge

- PLOT

- Email
"""


########################################################################
############################# Main Program #############################
########################################################################

def obspyDMT(**kwargs):
    
    """
    obspyDMT: is the function dedicated to the main part of the code.
    
    To run this program you have different options:
    1. External INPUT file ---> following files should be in the same 
       folder as obspyDMT:
    * INPUT.cfg
    * INPUT-Periods (Required for parallel requests)
    2. Command line (Please type "./obspyDMT.py --help" for more information)
    3. Imported and called with appropriate keyword arguments in other scripts.
    * There are no real checks for the keywords, so be sure to get them right.
    
    Parameters
    ----------
    :type input: dictionary
    :param input: a dictionary contains all inputs (default and user-defined)
    :type events: str, optional
    :param end: End time of event query timeframe. obspy.core.UTCDateTime
        recognizable string.
    
    Saves waveform data or metadata into folder structure.

    .. rubric:: Example

        >>> from obspyDMT import main as obspyDMT
        >>> obspyDMT(datapath="van", magmin=7, start="2011-10-23", force=True)
        Downloading NERIES eventlist... Keypress capture thread initialized...
        Press 'q' at any time to finish the file in progress and quit.
        done.
        Received 1 event(s) from NERIES.
        Downloading ArcLink inventory data...
        (...)

    .. rubric:: Notes

         See obspyDMT's help functions (command line: obspyDMT -h and
         obspyDMT -H) as well as the obspyDMT manual (available on the ObsPy
         SVN server) for further documentation.
    """ 
    
    print '------------------------------------------------------------' + \
            '---------------------'
    bold = "\033[1m"
    reset = "\033[0;0m"
    print '\t\t' + bold + 'ObsPyDMT ' + reset + '(' + bold + 'ObsPy D' + \
        reset + 'ata '+ bold + 'M' + reset + 'anagement' + bold + 'T' + \
        reset + 'ool)' + reset + '\n'
    print '\t' + 'Automatic tool for Downloading, Processing and Management'
    print '\t\t\t' + 'of Large Seismic Datasets'
    print '\n'
    print ':copyright:'
    print 'The ObsPy Development Team (devs@obspy.org)' + '\n'
    print 'Developed by Kasra Hosseini'
    print 'email: hosseini@geophysik.uni-muenchen.de' + '\n'
    print ':license:'
    print 'GNU General Public License, Version 3'
    print '(http://www.gnu.org/licenses/gpl-3.0-standalone.html)'
    print '------------------------------------------------------------' + \
            '---------------------'
    
    # global variables
    global input, events
    
    # ------------------Parsing command-line options--------------------
    (options, args, parser) = command_parse()
    
    # ------------------Read INPUT file (Parameters)--------------------
    if options.type == 'file':
        read_input_file()
    else:
        read_input_command(parser)
    import ipdb; ipdb.set_trace()
    # ------------------Parallel Requests-------------------------------
    if input['nodes'] == 'Y' and input['input_period'] != 'Y':
        nodes(input)
    
    # ------------------Getting List of Events/Continuous requests------
    if input['get_events'] == 'Y':
        get_Events(input, request = 'event-based')
    
    if input['get_continuous'] == 'Y':
        get_Events(input, request = 'continuous')
    
    # ------------------Generate desired INPUT-Periods file-------------
    if input['input_period'] == 'Y':
        INPUT_Periods_file(input)
    
    # ------------------IRIS--------------------------------------------
    if input['IRIS'] == 'Y':
        
        print '********************************************************'
        print 'IRIS -- Download waveforms, response files and meta-data'
        print '********************************************************'
        
        Stas_iris = IRIS_network(input)
        
        Stas_iris_target = []
        for stas in Stas_iris:
            if stas:
                Stas_iris_target.append(stas)
        
        if Stas_iris_target:
            IRIS_waveform(input, Stas_iris_target, type = 'save')
        else:
            'No available station in IRIS for your request!'
            
    # ------------------Arclink-----------------------------------------
    if input['ArcLink'] == 'Y':
            
        print '********************************************************'
        print 'ArcLink -- Download waveforms, response files and meta-data'
        print '********************************************************'
        
        Stas_arc = ARC_network(input)
        
        Stas_arc_target = []
        for stas in Stas_arc:
            if stas:
                Stas_arc_target.append(stas)
        
        if Stas_arc_target:
            ARC_waveform(input, Stas_arc_target, type = 'save')
        else:
            'No available station in ArcLink for your request!'
                
    # ------------------IRIS-Updating-----------------------------------
    if input['iris_update'] != 'N':
        
        print '*********************'
        print 'IRIS -- Updating Mode'
        print '*********************'
        
        Sta_req = IRIS_update(input, address = input['iris_update'])
        
        Stas_iris_target = []
        for stas in Sta_req:
            if stas:
                Stas_iris_target.append(stas)
        
        if Stas_iris_target:
            IRIS_waveform(input, Stas_iris_target, type = 'update')
        else:
            'No available station in IRIS for your request!'

    # ------------------ArcLink-Updating--------------------------------
    if input['arc_update'] != 'N':
        
        print '************************'
        print 'ArcLink -- Updating Mode'
        print '************************'
        
        Sta_req = ARC_update(input, address = input['arc_update'])
        
        Stas_arc_target = []
        for stas in Sta_req:
            if stas:
                Stas_arc_target.append(stas)
        
        if Stas_arc_target:
            ARC_waveform(input, Stas_arc_target, type = 'update')
        else:
            'No available station in ArcLink for your request!'
    
    # ------------------IRIS-instrument---------------------------------
    if input['iris_ic'] != 'N' or input['iris_ic_auto'] == 'Y':
        
        print '*****************************'
        print 'IRIS -- Instrument Correction'
        print '*****************************'
        
        IRIS_ARC_IC(input, clients = 'iris')
    
    # ------------------Arclink-instrument------------------------------
    if input['arc_ic'] != 'N' or input['arc_ic_auto'] == 'Y':
            
        print '********************************'
        print 'ArcLink -- Instrument Correction'
        print '********************************'
                
        IRIS_ARC_IC(input, clients = 'arc')
    
    # ------------------IRIS-merge--------------------------------------    
    if input['iris_merge'] != 'N' or input['iris_merge_auto'] == 'Y':
        
        print '*****************************'
        print 'IRIS -- Merging the waveforms'
        
        IRIS_ARC_merge(input, clients = 'iris')
    
    # ------------------ArcLink-merge-----------------------------------    
    if input['arc_merge'] != 'N' or input['arc_merge_auto'] == 'Y':
        
        print '********************************'
        print 'ArcLink -- Merging the waveforms'
            
        IRIS_ARC_merge(input, clients = 'arc')
    
    # ------------------PLOT--------------------------------------------    
    for i in ['plot_se', 'plot_sta', 'plot_ev', 'plot_ray', 'plot_epi']:
        if input[i] != 'N':
    
            print '*********************'
            print 'Start the PLOT module'
            print '*********************'
            
            if input['plot_all'] == 'Y' or input['plot_iris'] == 'Y':
                PLOT(input, clients = 'iris')
            if input['plot_arc'] == 'Y':
                PLOT(input, clients = 'arc')
    
    # ------------------Email-------------------------------------------    
    if input['email'] == 'Y':
        
        print '*********************************************'
        print 'Sending email to the following email-address:'
        print input['email_address']
        print '*********************************************'
        
        send_email(input, t1_pro)
        
    # ------------------Report------------------------------------------    
    if input['report'] == 'Y':
        
        print '******************************************'
        print 'Generating Report in the following folder:'
        print os.path.join(input['datapath'], 'REPORT')
        print '******************************************'
        
        report_DMT(input)
    
    # ------------------------------------------------------------------
    print '------------------------------------------------------------'
    print 'Thanks for using:' + '\n' 
    bold = "\033[1m"
    reset = "\033[0;0m"
    print '\t\t' + bold + 'ObsPyDMT ' + reset + '(' + bold + 'ObsPy D' + \
        reset + 'ata '+ bold + 'M' + reset + 'anagement ' + bold + 'T' + \
        reset + 'ool)' + reset + '\n'
    print '------------------------------------------------------------'


########################################################################
###################### Functions are defined here ######################
########################################################################

###################### command_parse ###################################

def command_parse():
    
    """
    Parsing command-line options.
    """
    
    # create command line option parser
    parser = OptionParser("%prog [options]")
    
    # configure command line options
    # action=".." tells OptionsParser what to save:
    # store_true saves bool TRUE,
    # store_false saves bool FALSE, store saves string; into the variable
    # given with dest="var"
    # * you need to provide every possible option here.
    
    helpmsg = "Shows the version of obspyDMT and quit the program"
    parser.add_option("--version", action="store_true",
                      dest="version", help=helpmsg)
                      
    helpmsg = "obspyDMT reads the inputs from command line " + \
                "('--type command' also [default]) or " + \
                "from external file: INPUT.cfg ('--type file')"
    parser.add_option("--type", action="store",
                      dest="type", help=helpmsg)
    
    helpmsg = "If the datapath is found deleting it before " + \
                "running obspyDMT."
    parser.add_option("--reset", action="store_true",
                      dest="reset", help=helpmsg)
    
    helpmsg = "The path where obspyDMT will store the data (default " + \
                "is ./obspyDMT-data)"
    parser.add_option("--datapath", action="store",
                      dest="datapath", help=helpmsg)
    
    helpmsg = "Start time. Default: 10 days ago."
    parser.add_option("--min_date", action="store",
                      dest="min_date", help=helpmsg)
    
    helpmsg = "End time. Default: 5 days ago."
    parser.add_option("--max_date", action="store",
                      dest="max_date", help=helpmsg)
    
    helpmsg = "Minimum magnitude. Default: 6.0"
    parser.add_option("--min_mag", action="store",
                      dest="min_mag", help=helpmsg)
    
    helpmsg = "Maximum magnitude. Default: 9.9"
    parser.add_option("--max_mag", action="store",
                      dest="max_mag", help=helpmsg)

    helpmsg = "Minimum depth. Default: 10.0 (above the surface)"
    parser.add_option("--min_depth", action="store",
                      dest="min_depth", help=helpmsg)
    
    helpmsg = "Maximum depth. Default: -6000.0"
    parser.add_option("--max_depth", action="store",
                      dest="max_depth", help=helpmsg)
    
    helpmsg = "Event-based request (Please refer to the tutorial)" + \
                ".Default: 'Y'"
    parser.add_option("--get_events", action="store",
                      dest="get_events", help=helpmsg)
    
    helpmsg = "Continuous request (Please refer to the tutorial)" + \
                ".Default: 'N'"
    parser.add_option("--continuous", action="store_true",
                      dest="get_continuous", help=helpmsg)
    
    helpmsg = "Time interval for dividing the continuous request. " + \
                "Default: 1 day"
    parser.add_option("--interval", action="store",
                      dest="interval", help=helpmsg)
    
    helpmsg = "IRIS bulkdataselect"
    parser.add_option("--iris_bulk", action="store_true",
                      dest="iris_bulk", help=helpmsg)
    
    helpmsg = "Waveform request."
    parser.add_option("--waveform", action="store",
                      dest="waveform", help=helpmsg)
    
    helpmsg = "Response file request"
    parser.add_option("--response", action="store",
                      dest="response", help=helpmsg)
    
    helpmsg = "Request from IRIS"
    parser.add_option("--iris", action="store",
                      dest="IRIS", help=helpmsg)
    
    helpmsg = "Request from ArcLink"
    parser.add_option("--arc", action="store",
                      dest="ArcLink", help=helpmsg)
                      
    helpmsg = "Parallel mode (Please refer to the tutorial)" + '\n' + \
                "min_date, max_date, min_mag, max_mag will be " + \
                "selected based on 'INPUT-Periods' file"
    parser.add_option("--nodes", action="store_true",
                      dest="nodes", help=helpmsg)
    
    helpmsg = "Generating the input_period file required for parallel " + \
                "requests (Please refer to the tutorial)"
    parser.add_option("--input_period", action="store_true",
                      dest="input_period", help=helpmsg)
    
    helpmsg = "SAC format for saving the waveforms. Default: MSEED"
    parser.add_option("--SAC", action="store_true",
                      dest="SAC", help=helpmsg)
    
    helpmsg = "Generating a date-time file for the IRIS request."
    parser.add_option("--time_iris", action="store_true",
                      dest="time_iris", help=helpmsg)
    
    helpmsg = "Generating a date-time file for the ArcLink request."
    parser.add_option("--time_arc", action="store_true",
                      dest="time_arc", help=helpmsg)
    
    helpmsg = "Time parameter in seconds which determines how close " + \
                "the event data will be cropped before the origin time. " + \
                "Default: 0 seconds."
    parser.add_option("--preset", action="store",
                      dest="preset", help=helpmsg)
    
    helpmsg = "Time parameter in seconds which determines how close " + \
                "the event data will be cropped after the origin time. " + \
                "Default: 1800 seconds."
    parser.add_option("--offset", action="store",
                      dest="offset", help=helpmsg)
    
    helpmsg = "Identity code restriction, syntax: net.sta.loc.cha (" + \
                "alternative to -N -S -L -C)."
    parser.add_option("--identity", action="store", dest="identity",
                        help=helpmsg)
    
    helpmsg = "Network code"
    parser.add_option("--net", action="store",
                      dest="net", help=helpmsg)
    
    helpmsg = "Station code"
    parser.add_option("--sta", action="store",
                      dest="sta", help=helpmsg)
    
    helpmsg = "Location code"
    parser.add_option("--loc", action="store",
                      dest="loc", help=helpmsg)
    
    helpmsg = "Channel code"
    parser.add_option("--cha", action="store",
                      dest="cha", help=helpmsg)
                      
    helpmsg = "Provide event rectangle with GMT syntax: <lonmin>/<lonmax>/" + \
                "<latmin>/<latmax>"
    parser.add_option("--event_rect", action="store", dest="event_rect",
                        help=helpmsg)
    
    helpmsg = "Maximum results for event request"
    parser.add_option("--max_result", action="store",
                      dest="max_result", help=helpmsg)
       
    helpmsg = "Provide station rectangle with GMT syntax: <lonmin>/<lonmax>/" \
                + "<latmin>/<latmax>"
    parser.add_option("--station_rect", action="store", 
                      dest="station_rect", help=helpmsg)
    
    helpmsg = "Longitude, Latitude and min, max radius for " + \
                "geographical station restriction. May not be used " + \
                "together with rectangular bounding box station " + \
                "restrictions. Syntax: -l lon/lat/rmin/rmax"
    parser.add_option("--station_circle", action="store",
                      dest="station_circle", help=helpmsg)
   
    helpmsg = "To test obspyDMT"
    parser.add_option("--test", action="store",
                      dest="test", help=helpmsg)
    
    helpmsg = "Update IRIS folder"
    parser.add_option("--iris_update", action="store",
                      dest="iris_update", help=helpmsg)
    
    helpmsg = "Update ArcLink folder"
    parser.add_option("--arc_update", action="store",
                      dest="arc_update", help=helpmsg)
    
    helpmsg = "Update all folders"
    parser.add_option("--update_all", action="store",
                      dest="update_all", help=helpmsg)
    
    helpmsg = "Apply Instrument Correction to IRIS folder"
    parser.add_option("--iris_ic", action="store",
                        dest="iris_ic", help=helpmsg)
    
    helpmsg = "Apply Instrument Correction to IRIS folder automatically"
    parser.add_option("--iris_ic_auto", action="store",
                        dest="iris_ic_auto", help=helpmsg)
    
    helpmsg = "Apply Instrument Correction to ArcLink folder"
    parser.add_option("--arc_ic", action="store",
                        dest="arc_ic", help=helpmsg)
    
    helpmsg = "Apply Instrument Correction to ArcLink folder automatically"
    parser.add_option("--arc_ic_auto", action="store",
                        dest="arc_ic_auto", help=helpmsg)
    
    helpmsg = "Apply Instrument Correction to all folders"
    parser.add_option("--ic_all", action="store",
                        dest="ic_all", help=helpmsg)
    
    helpmsg = "Do not apply Instrument Correction"
    parser.add_option("--ic_no", action="store_true",
                        dest="ic_no", help=helpmsg)
                        
    helpmsg = "Apply a bandpass filter to the data trace before " + \
                "deconvolution (None if you do not need filter in this step)"
    parser.add_option("--pre_filt", action="store",
                      dest="pre_filt", help=helpmsg)
    
    helpmsg = "Units to return response in. Can be either DIS (m), " + \
                "VEL (m/s) or ACC (m/s^2)"
    parser.add_option("--corr_unit", action="store",
                      dest="corr_unit", help=helpmsg)
    
    helpmsg = "Merging IRIS folders"
    parser.add_option("--iris_merge", action="store",
                        dest="iris_merge", help=helpmsg)
    
    helpmsg = "Merging IRIS folders automatically"
    parser.add_option("--iris_merge_auto", action="store",
                        dest="iris_merge_auto", help=helpmsg)
    
    helpmsg = "Merging folders -- Corrected or Raw?"
    parser.add_option("--merge_folder", action="store",
                        dest="merge_folder", help=helpmsg)
    
    helpmsg = "Merging ArcLink folders"
    parser.add_option("--arc_merge", action="store",
                        dest="arc_merge", help=helpmsg)
                    
    helpmsg = "Merging ArcLink folders automatically"
    parser.add_option("--arc_merge_auto", action="store",
                        dest="arc_merge_auto", help=helpmsg)
    
    helpmsg = "Merge all folders"
    parser.add_option("--merge_all", action="store",
                      dest="merge_all", help=helpmsg)
        
    helpmsg = "Do not merge"
    parser.add_option("--merge_no", action="store_true",
                      dest="merge_no", help=helpmsg)
   
    helpmsg = "Compress Raw counts files after instrument correction"
    parser.add_option("--zip_w", action="store_true",
                        dest="zip_w", help=helpmsg)
    
    helpmsg = "Compress Response files after instrument correction"
    parser.add_option("--zip_r", action="store_true",
                        dest="zip_r", help=helpmsg)
    
    helpmsg = "Plot folders -- Corrected or Raw?"
    parser.add_option("--plot_folder", action="store",
                        dest="plot_folder", help=helpmsg)
    
    helpmsg = "Plot all clients"
    parser.add_option("--plot_all", action="store",
                      dest="plot_all", help=helpmsg)
    
    helpmsg = "Plot IRIS"
    parser.add_option("--plot_iris", action="store_true",
                      dest="plot_iris", help=helpmsg)
    
    helpmsg = "Plot ARC"
    parser.add_option("--plot_arc", action="store_true",
                      dest="plot_arc", help=helpmsg)
    
    helpmsg = "Plot the events"
    parser.add_option("--plot_ev", action="store",
                      dest="plot_ev", help=helpmsg)
                      
    helpmsg = "Plot the stations"
    parser.add_option("--plot_sta", action="store",
                      dest="plot_sta", help=helpmsg)
                      
    helpmsg = "Plot both events and stations"
    parser.add_option("--plot_se", action="store",
                      dest="plot_se", help=helpmsg)
                      
    helpmsg = "Plot both events and stations + ray path"
    parser.add_option("--plot_ray", action="store",
                      dest="plot_ray", help=helpmsg)

    helpmsg = "Plot the epicentral-time"
    parser.add_option("--plot_epi", action="store",
                      dest="plot_epi", help=helpmsg)
                      
    helpmsg = "Minimum epicentral distance"
    parser.add_option("--min_epi", action="store",
                      dest="min_epi", help=helpmsg)
    
    helpmsg = "Maximum epicentral distance"
    parser.add_option("--max_epi", action="store",
                      dest="max_epi", help=helpmsg)
    
    helpmsg = "Address to save the plot."
    parser.add_option("--plot_save", action="store",
                      dest="plot_save", help=helpmsg)
    
    helpmsg = "Format of the saved plot."
    parser.add_option("--plot_format", action="store",
                      dest="plot_format", help=helpmsg)
    
    helpmsg = "Send an email to the specified email address after " + \
                "completing the job."
    parser.add_option("--email", action="store_true",
                      dest="email", help=helpmsg)
    
    helpmsg = "email address"
    parser.add_option("--email_address", action="store",
                      dest="email_address", help=helpmsg)
    
    helpmsg = "Generate a report after completing the job"
    parser.add_option("--report", action="store_true",
                      dest="report", help=helpmsg)
    
    # parse command line options
    (options, args) = parser.parse_args()
    
    return options, args, parser

###################### read_input_command ##############################

def read_input_command(parser):
    
    """
    Create input object (dictionary) based on command-line options.
    The default values are as "input" object (below) 
    [same in INPUT-default.cfg]
    """
    
    global input
    
    # Defining the default values. 
    # Each of these values could be changed:
    # 1. By changing the 'INPUT.cfg' file (if you use 
    # "'./obspyDMT.py --type file'")
    # 2. By defining the required command-line flag (if you use 
    # "'./obspyDMT.py --type command'")
    input = {   'datapath': 'obspyDMT-data',
                
                'min_date': str(UTCDateTime() - 60 * 60 * 24 * 10 * 1),
                'max_date': str(UTCDateTime() - 60 * 60 * 24 * 5 * 1),
                'min_mag': 5.5, 'max_mag': 9.9,
                'min_depth': +10.0, 'max_depth': -6000.0,
                
                'get_events': 'Y',
                'interval': 3600*24,
                
                'waveform': 'Y', 'response': 'Y',
                'IRIS': 'Y', 'ArcLink': 'Y',
                
                'preset': 0.0, 'offset': 1800.0,
                
                'net': '*', 'sta': '*', 'loc': '*', 'cha': '*',
                
                'evlatmin': -90.0, 'evlatmax': +90.0, 
                'evlonmin': -180.0, 'evlonmax': +180.0,
                
                'max_result': 2500,
                
                'lat_cba': None, 'lon_cba': None, 
                'mr_cba': None, 'Mr_cba': None,
                
                'mlat_rbb': None, 'Mlat_rbb': None, 
                'mlon_rbb': None, 'Mlon_rbb': None,

                'test': 'N',
                
                'iris_update': 'N', 'arc_update': 'N', 'update_all': 'N',

                'email_address': '',
                
                'ic_all': 'N',
                
                'iris_ic': 'N', 'iris_ic_auto': 'Y',
                'arc_ic': 'N', 'arc_ic_auto': 'Y',
                'pre_filt': '(0.008, 0.012, 3.0, 4.0)',
                'corr_unit': 'DIS',
                
                'merge_all': 'N',
                
                'iris_merge': 'N', 'iris_merge_auto': 'Y',
                'merge_folder': 'raw',
                
                'arc_merge': 'N', 'arc_merge_auto': 'Y',
                
                'plot_all': 'Y',
                'plot_folder': 'raw',
                
                'plot_ev': 'N', 'plot_sta': 'N', 'plot_se': 'N',
                'plot_ray': 'N', 'plot_epi': 'N',
                'plot_save': '.', 'plot_format': 'png',
                
                'min_epi': 0.0, 'max_epi': 180.0,
                
            }
    
    # feed input dictionary of defaults into parser object
    parser.set_defaults(**input)
    
    # parse command line options
    (options, args) = parser.parse_args()
    # command line options can now be accessed via options.varname.
    
    # parse datapath (check if given absolute or relative)
    if options.version: 
        bold = "\033[1m"
        reset = "\033[0;0m"
        print '\t\t' + '*********************************'
        print '\t\t' + '*        obspyDMT version:      *' 
        print '\t\t' + '*' + '\t\t' + bold + '1.0' + reset + '\t\t' + '*'
        print '\t\t' + '*********************************'
        print '\n'
        sys.exit(2)
        
    if options.datapath:
        if not os.path.isabs(options.datapath):
            options.datapath = os.path.join(os.getcwd(), options.datapath)
    
    if options.iris_update != 'N':
        if not os.path.isabs(options.iris_update):
            options.iris_update = os.path.join(os.getcwd(), options.iris_update)
    
    if options.arc_update != 'N':
        if not os.path.isabs(options.arc_update):
            options.arc_update = os.path.join(os.getcwd(), options.arc_update)
    
    if options.update_all != 'N':
        if not os.path.isabs(options.update_all):
            options.update_all = os.path.join(os.getcwd(), options.update_all)
    
    if options.iris_ic != 'N':
        if not os.path.isabs(options.iris_ic):
            options.iris_ic = os.path.join(os.getcwd(), options.iris_ic)
    
    if options.arc_ic != 'N':
        if not os.path.isabs(options.arc_ic):
            options.arc_ic = os.path.join(os.getcwd(), options.arc_ic)
    
    if options.ic_all != 'N':
        if not os.path.isabs(options.ic_all):
            options.ic_all = os.path.join(os.getcwd(), options.ic_all)
    
    if options.iris_merge != 'N':
        if not os.path.isabs(options.iris_merge):
            options.iris_merge = os.path.join(os.getcwd(), options.iris_merge)
    
    if options.arc_merge != 'N':
        if not os.path.isabs(options.arc_merge):
            options.arc_merge = os.path.join(os.getcwd(), options.arc_merge)
    
    if options.merge_all != 'N':
        if not os.path.isabs(options.merge_all):
            options.merge_all = os.path.join(os.getcwd(), options.merge_all)
    
    if options.plot_ev != 'N':
        if not os.path.isabs(options.plot_ev):
            options.plot_ev = os.path.join(os.getcwd(), options.plot_ev)
            
    if options.plot_sta != 'N':
        if not os.path.isabs(options.plot_sta):
            options.plot_sta = os.path.join(os.getcwd(), options.plot_sta)
    
    if options.plot_se != 'N':
        if not os.path.isabs(options.plot_se):
            options.plot_se = os.path.join(os.getcwd(), options.plot_se)
    
    if options.plot_ray != 'N':
        if not os.path.isabs(options.plot_ray):
            options.plot_ray = os.path.join(os.getcwd(), options.plot_ray)
    
    if options.plot_epi != 'N':
        if not os.path.isabs(options.plot_epi):
            options.plot_epi = os.path.join(os.getcwd(), options.plot_epi)
    
    if options.plot_save != 'N':
        if not os.path.isabs(options.plot_save):
            options.plot_save = os.path.join(os.getcwd(), options.plot_save)
    
    
    # extract min. and max. longitude and latitude if the user has given the
    # coordinates with -r (GMT syntax)
    if options.event_rect:
        try:
            options.event_rect = options.event_rect.split('/')
            if len(options.event_rect) != 4:
                print "Erroneous rectangle given."
                sys.exit(2)
            options.evlonmin = float(options.event_rect[0])
            options.evlonmax = float(options.event_rect[1])
            options.evlatmin = float(options.event_rect[2])
            options.evlatmax = float(options.event_rect[3])
        except:
            print "Erroneous rectangle given."
            sys.exit(2)
    
    # extract min. and max. longitude and latitude if the user has given the
    # coordinates with -g (GMT syntax)
    if options.station_rect:
        try:
            options.station_rect = options.station_rect.split('/')
            if len(options.station_rect) != 4:
                print "Erroneous rectangle given."
                sys.exit(2)
            options.mlon_rbb = float(options.station_rect[0])
            options.Mlon_rbb = float(options.station_rect[1])
            options.mlat_rbb = float(options.station_rect[2])
            options.Mlat_rbb = float(options.station_rect[3])
        except:
            print "Erroneous rectangle given."
            sys.exit(2)
    
    # circular station restriction option parsing
    if options.station_circle:
        try:
            options.station_circle = options.station_circle.split('/')
            if len(options.station_circle) != 4:
                print "Erroneous circle given."
                sys.exit(2)
            options.lon_cba = float(options.station_circle[0])
            options.lat_cba = float(options.station_circle[1])
            options.mr_cba = float(options.station_circle[2])
            options.Mr_cba = float(options.station_circle[3])
        except:
            print "Erroneous circle given."
            sys.exit(2)
    
    # delete data path if -R or --reset args are given at cmdline
    if options.reset:
        # try-except so we don't get an exception if path doesnt exist
        try:
            shutil.rmtree(options.datapath)
            print '----------------------------------'
            print 'The following folder has been deleted:'
            print str(options.datapath)
            print 'obspyDMT is going to create a new folder...'
            print '----------------------------------'
        except:
            pass
    
    # Extract network, station, location, channel if the user has given an
    # identity code (-i xx.xx.xx.xx)
    if options.identity:
        try:
            options.net, options.sta, options.loc, options.cha = \
                                    options.identity.split('.')
        except:
            print "Erroneous identity code given."
            sys.exit(2)
    
    input['datapath'] = options.datapath
    
    input['min_date'] = options.min_date
    input['max_date'] = options.max_date
    input['min_mag'] = float(options.min_mag)
    input['max_mag'] = float(options.max_mag)
    input['min_depth'] = float(options.min_depth)
    input['max_depth'] = float(options.max_depth)
        
    input['evlonmin'] = options.evlonmin
    input['evlonmax'] = options.evlonmax
    input['evlatmin'] = options.evlatmin
    input['evlatmax'] = options.evlatmax
    
    input['preset'] = float(options.preset)
    input['offset'] = float(options.offset)
    input['max_result'] = int(options.max_result)
    
    input['get_events'] = options.get_events
    
    if options.get_continuous:
        input['get_events'] = 'N'
        input['get_continuous'] = 'Y'
    else:
        input['get_continuous'] = 'N'
    input['interval'] = float(options.interval)
    
    if options.iris_bulk: options.iris_bulk = 'Y'
    input['iris_bulk'] = options.iris_bulk
    
    input['waveform'] = options.waveform
    input['response'] = options.response
    if options.SAC: options.SAC = 'Y'
    input['SAC'] = options.SAC
    
    input['IRIS'] = options.IRIS
    input['ArcLink'] = options.ArcLink
    
    if options.time_iris: options.time_iris = 'Y'
    input['time_iris'] = options.time_iris
    if options.time_arc: options.time_arc = 'Y'
    input['time_arc'] = options.time_arc
    
    if options.input_period: options.input_period = 'Y'
    input['input_period'] = options.input_period
    if options.nodes: options.nodes = 'Y'
    input['nodes'] = options.nodes
    
    input['net'] = options.net
    input['sta'] = options.sta
    if options.loc == "''":
        input['loc'] = ''
    elif options.loc == '""':
        input['loc'] = ''
    else:
        input['loc'] = options.loc
    
    input['cha'] = options.cha

    input['lon_cba'] = options.lon_cba
    input['lat_cba'] = options.lat_cba
    input['mr_cba'] = options.mr_cba
    input['Mr_cba'] = options.Mr_cba
    
    input['mlon_rbb'] = options.mlon_rbb
    input['Mlon_rbb'] = options.Mlon_rbb
    input['mlat_rbb'] = options.mlat_rbb
    input['Mlat_rbb'] = options.Mlat_rbb    
    
    if options.test != 'N':
        input['test'] = 'Y'
        input['test_num'] = int(options.test)
    
    input['iris_update'] = options.iris_update
    input['arc_update'] = options.arc_update
    input['update_all'] = options.update_all
    
    if input['update_all'] != 'N':
        input['iris_update'] = input['update_all']
        input['arc_update'] = input['update_all']
    
    input['iris_ic'] = options.iris_ic
    input['iris_ic_auto'] = options.iris_ic_auto
    
    input['arc_ic'] = options.arc_ic
    input['arc_ic_auto'] = options.arc_ic_auto
    
    input['ic_all'] = options.ic_all
    
    if input['ic_all'] != 'N':
        input['iris_ic'] = input['ic_all']
        input['arc_ic'] = input['ic_all']
    
    input['iris_merge'] = options.iris_merge
    input['arc_merge'] = options.arc_merge
    input['merge_all'] = options.merge_all
    
    if input['merge_all'] != 'N':
        input['iris_merge'] = input['merge_all']
        input['arc_merge'] = input['merge_all']
        
    if options.zip_w: options.zip_w = 'Y'
    input['zip_w'] = options.zip_w
    
    if options.zip_r: options.zip_r = 'Y'
    input['zip_r'] = options.zip_r
    
    input['plot_folder'] = options.plot_folder
    
    input['plot_all'] = options.plot_all
    if options.plot_iris: options.plot_iris = 'Y'
    input['plot_iris'] = options.plot_iris
    if options.plot_arc: options.plot_arc = 'Y'
    input['plot_arc'] = options.plot_arc
    
    input['plot_ev'] = options.plot_ev
    input['plot_sta'] = options.plot_sta
    input['plot_se'] = options.plot_se
    input['plot_ray'] = options.plot_ray
    input['plot_epi'] = options.plot_epi
    
    input['min_epi'] = float(options.min_epi)
    input['max_epi'] = float(options.max_epi)
    
    input['plot_save'] = options.plot_save
    input['plot_format'] = options.plot_format
        
    if options.email: options.email = 'Y'
    input['email'] = options.email
    input['email_address'] = options.email_address
    
    if options.report: options.report = 'Y'
    input['report'] = options.report
    
    input['corr_unit'] = options.corr_unit
    input['pre_filt'] = options.pre_filt
    
    #--------------------------------------------------------
    if input['get_continuous'] == 'N':
        input['iris_merge_auto'] = 'N'
        input['arc_merge_auto'] = 'N'
    else:
        input['iris_merge_auto'] = options.iris_merge_auto
        input['merge_folder'] = options.merge_folder
        input['arc_merge_auto'] = options.arc_merge_auto
    
    for i in ['iris_update', 'arc_update', 'iris_ic', 'arc_ic', \
                'iris_merge', 'arc_merge', 'plot_se', 'plot_sta', \
                'plot_ev', 'plot_ray', 'plot_epi']:
        if input[i] != 'N':
            input['get_events'] = 'N'
            input['get_continuous'] = 'N'
            input['IRIS'] = 'N'
            input['ArcLink'] = 'N'
            input['iris_ic_auto'] = 'N'
            input['arc_ic_auto'] = 'N'
            input['iris_merge_auto'] = 'N'
            input['arc_merge_auto'] = 'N'
    
    if options.IRIS == 'N':
        input['iris_ic_auto'] = 'N'
        input['iris_merge_auto'] = 'N'
    if options.ArcLink == 'N':
        input['arc_ic_auto'] = 'N'
        input['arc_merge_auto'] = 'N'
    
    if options.ic_no:
        input['iris_ic_auto'] = 'N'
        input['arc_ic_auto'] = 'N'
    
    if options.merge_no:
        input['iris_merge_auto'] = 'N'
        input['arc_merge_auto'] = 'N'
    
    if input['plot_iris'] == 'Y' or input['plot_arc'] == 'Y':
        input['plot_all'] = 'N'
        
###################### read_input_file #################################

def read_input_file():  
    
    """
    Read inputs from INPUT.cfg file.
    
    This module will read the INPUT.cfg file which is 
    located in the same folder as obspyDMT.py
    
    Please note that if you choose (nodes = Y) then:
    * min_datetime
    * max_datetime
    * min_magnitude
    * max_magnitude
    will be selected based on INPUT-Periods file.
    """
    
    global input
    
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(os.getcwd(), 'INPUT.cfg'))

    input = {}
    input['datapath'] = config.get('Address_info', 'datapath')
    input['inter_address'] = config.get('Address_info', 'interactive_address')
    input['target_folder'] = config.get('Address_info', 'target_folder')
    input['save_folder'] = config.get('Address_info', 'save_folder')
    
    if not os.path.isabs(input['datapath']):
        input['datapath'] = os.path.join(os.getcwd(), input['datapath'])
    
    if not os.path.isabs(input['inter_address']):
        input['inter_address'] = os.path.join(os.getcwd(), input['inter_address'])
    
    if not os.path.isabs(input['target_folder']):
        input['target_folder'] = os.path.join(os.getcwd(), input['target_folder'])
    
    if not os.path.isabs(input['save_folder']):
        input['save_folder'] = os.path.join(os.getcwd(), input['save_folder'])
        
    
    input['min_date'] = str(eval(config.get('Event_Request', 'min_datetime')))
    input['max_date'] = str(eval(config.get('Event_Request', 'max_datetime')))
    input['min_mag'] = config.getfloat('Event_Request', 'min_magnitude')
    input['max_mag'] = config.getfloat('Event_Request', 'max_magnitude')
    input['min_depth'] = config.getfloat('Event_Request', 'min_depth')
    input['max_depth'] = config.getfloat('Event_Request', 'max_depth')
    input['evlonmin'] = config.getfloat('Event_Request', 'evlonmin')
    input['evlonmax'] = config.getfloat('Event_Request', 'evlonmax')
    input['evlatmin'] = config.getfloat('Event_Request', 'evlatmin')
    input['evlatmax'] = config.getfloat('Event_Request', 'evlatmax')
    input['preset'] = config.getfloat('Event_Request', 'preset')
    input['offset'] = config.getfloat('Event_Request', 'offset')
    input['max_result'] = config.getint('Event_Request', 'max_results')
    
    input['get_events'] = config.get('Request', 'get_events')
    input['input_period'] = config.get('Parallel', 'input_period')
    input['IRIS'] = config.get('Request', 'IRIS')
    input['ArcLink'] = config.get('Request', 'ArcLink')
    input['time_iris'] = config.get('Request', 'time_iris')
    input['time_arc'] = config.get('Request', 'time_arc')
    
    input['nodes'] = config.get('Parallel', 'nodes')

    input['waveform'] = config.get('Request', 'waveform')
    input['response'] = config.get('Request', 'response')
    input['SAC'] = config.get('Request', 'SAC')
    
    input['net'] = config.get('specifications_request', 'network')
    input['sta'] = config.get('specifications_request', 'station')
    
    if config.get('specifications_request', 'location') == "''":
        input['loc'] = ''
    elif config.get('specifications_request', 'location') == '""':
        input['loc'] = ''
    else:
        input['loc'] = config.get('specifications_request', 'location')
    
    input['cha'] = config.get('specifications_request', 'channel')

    if config.get('specifications_request', 'lat') == 'None':
        input['lat_cba'] = None
    else:
        input['lat_cba'] = config.get('specifications_request', 'lat')
        
    if config.get('specifications_request', 'lon') == 'None':
        input['lon_cba'] = None
    else:
        input['lon_cba'] = config.get('specifications_request', 'lon')
    
    if config.get('specifications_request', 'minradius') == 'None':
        input['mr_cba'] = None
    else:
        input['mr_cba'] = config.get('specifications_request', 'minradius')
    
    if config.get('specifications_request', 'maxradius') == 'None':
        input['Mr_cba'] = None
    else:
        input['Mr_cba'] = config.get('specifications_request', 'maxradius')
    
        
    if config.get('specifications_request', 'minlat') == 'None':
        input['mlat_rbb'] = None
    else:
        input['mlat_rbb'] = config.get('specifications_request', 'minlat')
    
    if config.get('specifications_request', 'maxlat') == 'None':
        input['Mlat_rbb'] = None
    else:
        input['Mlat_rbb'] = config.get('specifications_request', 'maxlat')
    
    if config.get('specifications_request', 'minlon') == 'None':
        input['mlon_rbb'] = None
    else:
        input['mlon_rbb'] = config.get('specifications_request', 'minlon')
    
    if config.get('specifications_request', 'maxlon') == 'None':
        input['Mlon_rbb'] = None
    else:
        input['Mlon_rbb'] = config.get('specifications_request', 'maxlon')

    
    input['test'] = config.get('test', 'test')
    input['test_num'] = config.getint('test', 'test_num')
    
    input['update_interactive'] = config.get('update', 'update_interactive')
    input['iris_update'] = config.get('update', 'iris_update')
    input['arc_update'] = config.get('update', 'arc_update')

    input['QC_IRIS'] = config.get('QC', 'QC_IRIS')
    input['QC_ARC'] = config.get('QC', 'QC_ARC')
    
    input['email'] = config.get('email', 'email')
    input['email_address'] = config.get('email', 'email_address')
    
    input['report'] = config.get('report', 'report')
    
    input['corr_unit'] = config.get('instrument_correction', 'corr_unit')
    input['pre_filt'] = config.get('instrument_correction', 'pre_filter')
    
    input['plt_event'] = config.get('ObsPyPT', 'plot_event')
    input['plt_sta'] = config.get('ObsPyPT', 'plot_sta')
    input['plt_ray'] = config.get('ObsPyPT', 'plot_ray')

    input['llcrnrlon'] = config.getfloat('ObsPyPT', 'llcrnrlon')
    input['urcrnrlon'] = config.getfloat('ObsPyPT', 'urcrnrlon')
    input['llcrnrlat'] = config.getfloat('ObsPyPT', 'llcrnrlat')
    input['urcrnrlat'] = config.getfloat('ObsPyPT', 'urcrnrlat')
    
    input['lon_0'] = config.getfloat('ObsPyPT', 'lon_0')
    input['lat_0'] = config.getfloat('ObsPyPT', 'lat_0')
    
###################### nodes ###########################################

def nodes(input):
    
    """
    Downloading in Parallel way
    Please change the 'INPUT-Periods' file for different requests
    Suggestion: 
    Do not request more than 5 in parallel...
    """
    
    f = open(os.path.join(os.getcwd(), 'INPUT-Periods'))
    per_tty = f.readlines()
    
    for i in range(0, len(per_tty)):
        per_tty[i] = per_tty[i].split('_')
    
    if os.path.exists(os.path.join(input['datapath'], 'tty-info')) != True:
    
        if os.path.exists(input['datapath']) != True:
            os.makedirs(input['datapath'])
        
        print '--------------------------------------------------------'
        n = int(raw_input('Please enter a node number: (from 0 to ... ' + \
                'depends on INPUT-Periods.)' + '\n'))
        print '--------------------------------------------------------'
        
        tty = open(os.path.join(input['datapath'], 'tty-info'), 'a+')
        
        tty.writelines(commands.getoutput('hostname') + '  ,  ' + \
            commands.getoutput('tty') + '  ,  ' + per_tty[n][0] + \
            '_' + per_tty[n][1] + '_' + per_tty[n][2] + '_' + \
            per_tty[n][3][:-1] + '  ,  ' +  '\n')
        
        tty.close()     
        
    else:
        
        print '--------------------------------------------------------'
        n = int(raw_input('Please enter a node number: (from 0 to ... ' + \
                'depends on INPUT-Periods.)' + '\n' + '(If you enter "-1", ' + \
                'it means that the node number already exists in the ' + \
                '"tty-info" file.)' + '\n'))
        print '--------------------------------------------------------'
        
        if n == -1:
            print 'You entered "-1" -- the node number exists in the tty-info!'
            print '--------------------------------------------------------'
        else: 
            tty = open(os.path.join(input['datapath'], 'tty-info'), 'a')
            tty.writelines(commands.getoutput('hostname') + '  ,  ' + \
                    commands.getoutput('tty') + '  ,  ' + per_tty[n][0] + \
                    '_' + per_tty[n][1] + '_' + per_tty[n][2] + '_' + \
                    per_tty[n][3][:-1] + '  ,  ' +  '\n')

            tty.close()     
    
    tty = open(os.path.join(input['datapath'], 'tty-info'), 'r')
    tty_str = tty.readlines()
    
    for i in range(0, len(tty_str)):
        tty_str[i] = tty_str[i].split('  ,  ')
    
    for i in range(0, len(tty_str)):
        if commands.getoutput('hostname') == tty_str[i][0]:
            if commands.getoutput('tty') == tty_str[i][1]:
                
                input['min_date'] = tty_str[i][2].split('_')[0]
                input['max_date'] = tty_str[i][2].split('_')[1]
                input['min_mag'] = tty_str[i][2].split('_')[2]
                input['max_mag'] = tty_str[i][2].split('_')[3]
    
    print input['min_date']
    print input['max_date']
    print input['min_mag'] 
    print input['max_mag']
    
    return input

###################### INPUT_Periods_file ##############################

def INPUT_Periods_file(input):
    
    """
    This module is mainly written for Parallel requests.
    Generates the INPUT-Periods file based on requested events.
    
    This function makes the list of events 
    tb secs before and ta secs after each event.
    """
    
    global events
    
    tb = 3600
    ta = 3600
    
    Period = input['min_date'].split('T')[0] + '_' + \
                input['max_date'].split('T')[0] + '_' + \
                str(input['min_mag']) + '_' + str(input['max_mag'])
    eventpath = os.path.join(input['datapath'], Period)
    
    len_events = len(events)
    
    input_period = open(os.path.join(os.getcwd(), 'INPUT-Periods'), 'a+')

    for i in range(0, len_events):
        
        str_event = str(events[i]['datetime']-tb) + '_' + \
            str(events[i]['datetime']+ta) + '_' + \
            str(events[i]['magnitude'] - 0.01) + '_' + \
            str(events[i]['magnitude'] + 0.01) + '\n'
        input_period.writelines(str_event)
    
    input_period.close()
    
    print '************************************************************'    
    print 'New INPUT-Periods file is generated in your folder.'
    print 'Now, you could run the program again based on your desired event :)' 
    print '************************************************************'
    
    sys.exit()

###################### get_Events ######################################

def get_Events(input, request):
    
    """
    Getting list of events from NERIES
    
    NERIES: a client for the Seismic Data Portal (http://www.seismicportal.eu) 
    which was developed under the European Commission-funded NERIES project. 
    
    The Portal provides a single point of access to diverse, 
    distributed European earthquake data provided in a unique joint 
    initiative by observatories and research institutes in and around Europe.
    """
        
    t_event_1 = datetime.now()
    
    global events
    
    Period = input['min_date'].split('T')[0] + '_' + \
        input['max_date'].split('T')[0] + '_' + \
        str(input['min_mag']) + '_' + str(input['max_mag'])
    eventpath = os.path.join(input['datapath'], Period)
    
    if os.path.exists(eventpath) == True:
        print '--------------------------------------------------------'
        
        if raw_input('Folder for requested Period:' + '\n' + \
            str(eventpath) + \
            '\n' + 'exists in your directory.' + '\n\n' + \
            'You could either:' + '\n' + 'N: Close the program and try the ' + \
            'updating mode.' + '\n' + \
            'Y: Remove the tree, continue the program ' + \
            'and download again.' + \
            '\n\n' + 'Do you want to continue? (Y/N)' + '\n') == 'Y':
            print '--------------------------------------------------------'
            shutil.rmtree(eventpath)
            os.makedirs(eventpath)
        
        else:
            print '--------------------------------------------------------'
            print 'So...you decided to update your folder...Ciao'
            print '--------------------------------------------------------'
            sys.exit()
            
    else:
        os.makedirs(eventpath)
    
    events = events_info(request)
        
    os.makedirs(os.path.join(eventpath, 'EVENT'))
    len_events = len(events)
    
    print 'Length of the events found based on the inputs: ' + \
            str(len_events) + '\n'
    
    for i in range(0, len_events):
        print "Event No:" + " " + str(i+1)
        print "Date Time:" + " " + str(events[i]['datetime'])
        print "Depth:" + " " + str(events[i]['depth'])
        print "Event-ID:" + " " + events[i]['event_id']
        try:
            print "Flynn-Region:" + " " + events[i]['flynn_region']
        except Exception, e:
            print "Flynn-Region:" + " " + "NONE"
        print "Latitude:" + " " + str(events[i]['latitude'])
        print "Longitude:" + " " + str(events[i]['longitude'])
        print "Magnitude:" + " " + str(events[i]['magnitude'])
        print "-------------------------------------------------"
                
    Event_cat = open(os.path.join(eventpath, 'EVENT', 'EVENT-CATALOG'), 'a+')
    Event_cat.writelines(str(Period) + '\n')
    Event_cat.writelines('-------------------------------------' + '\n')
    Event_cat.writelines('Information about the requested Events:' + '\n\n')
    Event_cat.writelines('Number of Events: ' + str(len_events) + '\n')
    Event_cat.writelines('min datetime: ' + str(input['min_date']) + '\n')
    Event_cat.writelines('max datetime: ' + str(input['max_date']) + '\n')
    Event_cat.writelines('min magnitude: ' + str(input['min_mag']) + '\n')
    Event_cat.writelines('max magnitude: ' + str(input['max_mag']) + '\n')
    Event_cat.writelines('min latitude: ' + str(input['evlatmin']) + '\n')
    Event_cat.writelines('max latitude: ' + str(input['evlatmax']) + '\n')
    Event_cat.writelines('min longitude: ' + str(input['evlonmin']) + '\n')
    Event_cat.writelines('max longitude: ' + str(input['evlonmax']) + '\n')
    Event_cat.writelines('min depth: ' + str(input['min_depth']) + '\n')
    Event_cat.writelines('max depth: ' + str(input['max_depth']) + '\n')
    Event_cat.writelines('-------------------------------------' + '\n\n')
    Event_cat.close()
    
    
    for j in range(0, len_events):
        Event_cat = open(os.path.join(eventpath, 'EVENT', 'EVENT-CATALOG'), 'a')
        Event_cat.writelines("Event No: " + str(j) + '\n')
        Event_cat.writelines("Event-ID: " + str(events[j]['event_id']) + '\n')
        Event_cat.writelines("Date Time: " + str(events[j]['datetime']) + '\n')
        Event_cat.writelines("Magnitude: " + str(events[j]['magnitude']) + '\n')
        Event_cat.writelines("Depth: " + str(events[j]['depth']) + '\n')
        Event_cat.writelines("Latitude: " + str(events[j]['latitude']) + '\n')
        Event_cat.writelines("Longitude: " + str(events[j]['longitude']) + '\n')
        
        try:
            Event_cat.writelines("Flynn-Region: " + \
                                str(events[j]['flynn_region']) + '\n')
        
        except Exception, e:
            Event_cat.writelines("Flynn-Region: " + 'None' + '\n')
        
        Event_cat.writelines('-------------------------------------' + '\n')
        Event_cat.close()
    
    Event_file = open(os.path.join(eventpath, 'EVENT', 'event_list'), 'a+')
    pickle.dump(events, Event_file)
    Event_file.close()
    
    print 'Events are saved!'
    
    print 'Length of events: ' + str(len_events) + '\n'
    
    t_event_2 = datetime.now()
    t_event = t_event_2 - t_event_1
    
    print 'Time for getting and saving the events:'
    print t_event
    
    return events

###################### events_info #####################################

def events_info(request):
    
    """
    Get the event(s) info for event-based or continuous requests
    """
    
    global input
    
    if request == 'event-based':
        client_neries = Client_neries()
        
        events = client_neries.getEvents(min_datetime=input['min_date'], \
            max_datetime=input['max_date'], min_magnitude=input['min_mag'], \
            max_magnitude=input['max_mag'], min_latitude=input['evlatmin'], \
            max_latitude=input['evlatmax'], min_longitude=input['evlonmin'], \
            max_longitude=input['evlonmax'], min_depth = input['min_depth'], \
            max_depth=input['max_depth'], max_results=input['max_result'])
        
        for i in range(0, len(events)):
            events[i]['t1'] = events[i]['datetime'] - input['preset']
            events[i]['t2'] = events[i]['datetime'] + input['offset']
    
    elif request == 'continuous':
        m_date = UTCDateTime(input['min_date'])
        M_date = UTCDateTime(input['max_date'])
        
        t_cont = M_date - m_date
        
        events = []
            
        if t_cont > input['interval']:
            num_div = int(t_cont/input['interval'])
            t_res = t_cont - num_div*input['interval']
            
            for i in range(0, num_div):
                events.append({'author': 'NAN', 'event_id': 'continuous' + str(i), \
                            'origin_id': -12345.0, 'longitude': -12345.0, \
                            'datetime': m_date + i*input['interval'], \
                            't1': m_date + i*input['interval'],\
                            't2': m_date + (i+1)*input['interval'] + 60.0,\
                            'depth': -12345.0, 'magnitude': -12345.0, \
                            'magnitude_type': 'NAN', 'latitude': -12345.0, \
                            'flynn_region': 'NAN'})
                            
            events.append({'author': 'NAN', 'event_id': 'continuous' + str(i+1), \
                            'origin_id': -12345.0, 'longitude': -12345.0, \
                            'datetime': m_date + (i+1)*input['interval'], \
                            't1': m_date + (i+1)*input['interval'],\
                            't2': M_date,\
                            'depth': -12345.0, 'magnitude': -12345.0, \
                            'magnitude_type': 'NAN', 'latitude': -12345.0, \
                            'flynn_region': 'NAN'})
        else:
            events.append({'author': 'NAN', 'event_id': 'continuous0', \
                            'origin_id': -12345.0, 'longitude': -12345.0, \
                            'datetime': m_date, \
                            't1': m_date,\
                            't2': M_date,\
                            'depth': -12345.0, 'magnitude': -12345.0, \
                            'magnitude_type': 'NAN', 'latitude': -12345.0, \
                            'flynn_region': 'NAN'})

    return events

###################### IRIS_network ####################################

def IRIS_network(input):
    
    """
    Returns information about what time series data is available 
    at the IRIS DMC for all requested events
    """

    t_iris_1 = datetime.now()
    
    global events
    
    len_events = len(events)
    Period = input['min_date'].split('T')[0] + '_' + \
                input['max_date'].split('T')[0] + '_' + \
                str(input['min_mag']) + '_' + str(input['max_mag'])
    eventpath = os.path.join(input['datapath'], Period)
    
    create_foders_files(events, eventpath)

    print 'IRIS-Folders are Created!'
    print "--------------------"
    
    Stas_iris = []
    
    for i in range(0, len_events):
        
        target_path = os.path.join(eventpath, events[i]['event_id'])
        Sta_iris = IRIS_available(input, events[i], target_path, event_number = i)
        Stas_iris.append(Sta_iris)
        
        if input['iris_bulk'] != 'Y':
            print 'IRIS-Availability for event: ' + str(i+1) + str('/') + \
                                    str(len_events) + '  ---> ' + 'DONE'
        else:
            print 'IRIS-bulkfile for event    : ' + str(i+1) + str('/') + \
                                    str(len_events) + '  ---> ' + 'DONE'
        
        if input['get_continuous'] == 'Y' and input['iris_bulk'] == 'Y':
            for j in range(1, len_events):
                Stas_iris.append(Sta_iris)
                target_path = os.path.join(eventpath, events[j]['event_id'])
                shutil.copy2(os.path.join(eventpath, events[0]['event_id'], \
                    'info', 'bulkdata-0.txt'), \
                    os.path.join(target_path, \
                    'info', 'bulkdata-' + str(j) + '.txt'))
                print 'IRIS-Availability for event: ' + str(j+1) + str('/') + \
                                    str(len_events) + '  ---> ' + 'DONE'
            break
        
    t_iris_2 = datetime.now()
    t_iris = t_iris_2 - t_iris_1
    print "--------------------"
    print 'IRIS-Time: (Availability)'
    print t_iris    
    
    return Stas_iris

###################### IRIS_available ##################################

def IRIS_available(input, event, target_path, event_number):
    
    """
    Check the availablity of the IRIS stations
    """
    
    client_iris = Client_iris()
    Sta_iris = []
    
    try:       
            
        available = client_iris.availability(network=input['net'], \
            station=input['sta'], location=input['loc'], \
            channel=input['cha'], \
            starttime=UTCDateTime(event['t1']), \
            endtime=UTCDateTime(event['t2']), \
            lat=input['lat_cba'], \
            lon=input['lon_cba'], minradius=input['mr_cba'], \
            maxradius=input['Mr_cba'], minlat=input['mlat_rbb'], \
            maxlat=input['Mlat_rbb'], minlon=input['mlon_rbb'], \
            maxlon=input['Mlon_rbb'], output='xml')
        
        Sta_iris = XML_list_avail(xmlfile = available)
        
        if input['iris_bulk'] == 'Y':
        
            if os.path.exists(os.path.join(target_path,\
                                    'info', 'bulkdata-' + str(event_number) + '.txt')):
                print 'bulkdata-' + str(event_number) + '.txt' + ' exists in the directory!'
                print '--------------------------------------------------------------------'
            
            else:
                available_bulk = client_iris.availability(network=input['net'], \
                            station=input['sta'], location=input['loc'], \
                            channel=input['cha'], \
                            starttime=UTCDateTime(event['t1']), \
                            endtime=UTCDateTime(event['t2']), \
                            lat=input['lat_cba'], \
                            lon=input['lon_cba'], minradius=input['mr_cba'], \
                            maxradius=input['Mr_cba'], minlat=input['mlat_rbb'], \
                            maxlat=input['Mlat_rbb'], minlon=input['mlon_rbb'], \
                            maxlon=input['Mlon_rbb'], \
                            filename = os.path.join(target_path,\
                                        'info', 'bulkdata-' + str(event_number) + '.txt'),\
                                                                    output='bulk')
            
    except Exception, e:
        Exception_file = open(os.path.join(target_path, \
            'info', 'exception'), 'a+')
        ee = 'iris -- Event:' + str(event_number) + '---' + str(e) + '\n'
        
        Exception_file.writelines(ee)
        Exception_file.close()
        print e
        
    return Sta_iris
    
###################### IRIS_waveform ###############################

def IRIS_waveform(input, Sta_req, type):
    
    """
    Gets Waveforms, Response files and meta-data 
    from IRIS DMC based on the requested events...
    """
    
    t_wave_1 = datetime.now()
    
    global events
    
    client_iris = Client_iris()
    add_event = []
    
    if type == 'save':
        Period = input['min_date'].split('T')[0] + '_' + \
                    input['max_date'].split('T')[0] + '_' + \
                    str(input['min_mag']) + '_' + str(input['max_mag'])
        eventpath = os.path.join(input['datapath'], Period)
        for i in range(0, len(events)):
            add_event.append(os.path.join(eventpath, \
                                        events[i]['event_id'])) 
    elif type == 'update':
        events, add_event = quake_info(input['iris_update'], target = 'info')
    
    len_events = len(events)
    
    for i in range(0, len_events):
        print "--------------------"
        if input['test'] == 'Y':
            len_req_iris = input['test_num']
        else:   
            len_req_iris = len(Sta_req[i])

        
        if input['iris_bulk'] == 'Y':
                    
            bulk_file = os.path.join(add_event[i], 'info', \
                                'bulkdata-' + str(i) + '.txt')
            
            print 'bulkdataselect request is sent for event: ' + \
                                        str(i+1) + '/' + str(len_events)
            bulk_st = client_iris.bulkdataselect(bulk_file)
            
            print 'Saving the stations...'
            for m in range(0, len(bulk_st)):
                bulk_st_info = bulk_st[m].stats
                bulk_st[m].write(os.path.join(add_event[i], 'BH_RAW', \
                    bulk_st_info['network'] + '.' + \
                    bulk_st_info['station'] + '.' + \
                    bulk_st_info['location'] + '.' + \
                    bulk_st_info['channel']), 'MSEED')

            input['waveform'] = 'N'
            print 'bulkdataselect request is done for event: ' + \
                                        str(i+1) + '/' + str(len_events)

        dic = {}                
            
        for j in range(0, len_req_iris):
        
            print '------------------'
            print type
            print 'IRIS-Event and Station Numbers are:'
            print str(i+1) + '/' + str(len_events) + '-' + str(j+1) + '/' + \
                    str(len(Sta_req[i])) + '-' + input['cha']
            try:
                
                client_iris = Client_iris()
                
                t11 = datetime.now()
                
                if Sta_req[i][j][2] == '--' or Sta_req[i][j][2] == '  ':
                        Sta_req[i][j][2] = ''
                
                
                if input['waveform'] == 'Y':                    
                    
                    dummy = 'Waveform'
                    
                    client_iris.saveWaveform(os.path.join(add_event[i], 'BH_RAW', \
                        Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3]), \
                        Sta_req[i][j][0], Sta_req[i][j][1], \
                        Sta_req[i][j][2], Sta_req[i][j][3], \
                        events[i]['t1'], events[i]['t2'])
                    
                    print "Saving Waveform for: " + Sta_req[i][j][0] + \
                        '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + "  ---> DONE"  
                
                
                if input['response'] == 'Y':

                    dummy = 'Response'
                    
                    client_iris.saveResponse(os.path.join(add_event[i], \
                        'Resp', 'RESP' + '.' + \
                        Sta_req[i][j][0] +  '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3]), \
                        Sta_req[i][j][0], Sta_req[i][j][1], \
                        Sta_req[i][j][2], Sta_req[i][j][3], \
                        events[i]['t1'], events[i]['t2'])
                    
                    print "Saving Response for: " + Sta_req[i][j][0] + \
                        '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + "  ---> DONE"   
                     
                                
                dummy = 'Meta-data'
                
                dic[j] ={'info': Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + \
                    '.' + Sta_req[i][j][2] + '.' + Sta_req[i][j][3], \
                    'net': Sta_req[i][j][0], 'sta': Sta_req[i][j][1], \
                    'latitude': Sta_req[i][j][4], 'longitude': Sta_req[i][j][5], \
                    'loc': Sta_req[i][j][2], 'cha': Sta_req[i][j][3], \
                    'elevation': Sta_req[i][j][6], 'depth': 0}

                Syn_file = open(os.path.join(add_event[i], 'info', \
                                        'station_event'), 'a')
                syn = dic[j]['net'] + ',' + dic[j]['sta'] + ',' + \
                        dic[j]['loc'] + ',' + dic[j]['cha'] + ',' + \
                        dic[j]['latitude'] + ',' + dic[j]['longitude'] + \
                        ',' + dic[j]['elevation'] + ',' + '0' + ',' + \
                        events[i]['event_id'] + ',' + str(events[i]['latitude']) \
                        + ',' + str(events[i]['longitude']) + ',' + \
                        str(events[i]['depth']) + ',' + \
                        str(events[i]['magnitude']) + ',' + 'iris' + ',' + '\n'
                Syn_file.writelines(syn)
                Syn_file.close()
                
                if input['SAC'] == 'Y':
                    writesac(address_st = os.path.join(add_event[i], 'BH_RAW', \
                        Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3]), \
                        sta_info = dic[j], ev_info = events[i])
                
                print "Saving Metadata for: " + Sta_req[i][j][0] + \
                    '.' + Sta_req[i][j][1] + '.' + \
                    Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + "  ---> DONE"
                    
                
                t22 = datetime.now()
                    
                if input['time_iris'] == 'Y':
                    time_iris = t22 - t11
                    time_file = open(os.path.join(add_event[i], 'info', \
                        'iris_time'), 'a')
                    size = getFolderSize(os.path.join(add_event[i])) 
                    print size/1.e6
                    ti = Sta_req[i][j][0] + ',' + Sta_req[i][j][1] + ',' + \
                        Sta_req[i][j][2] + ',' + Sta_req[i][j][3] + ',' + \
                        str(time_iris.seconds) + ',' + str(time_iris.microseconds) \
                        + ',' + str(size/1.e6) + ',' + '\n'
                    time_file.writelines(ti)
                    time_file.close()
                
            except Exception, e:    
                
                t22 = datetime.now()
                    
                if input['time_iris'] == 'Y':
                    time_iris = t22 - t11
                    time_file = open(os.path.join(add_event[i], \
                                    'info', 'iris_time'), 'a')
                    size = getFolderSize(os.path.join(add_event[i])) 
                    print size/1.e6
                    ti = Sta_req[i][j][0] + ',' + Sta_req[i][j][1] + ',' + \
                        Sta_req[i][j][2] + ',' + Sta_req[i][j][3] + ',' + \
                        str(time_iris.seconds) + ',' + \
                        str(time_iris.microseconds) + ',' + str(size/1.e6) + ',' + '\n'
                    time_file.writelines(ti)
                    time_file.close()
                                
                print dummy + '---' + Sta_req[i][j][0] +    '.' + Sta_req[i][j][1] + \
                    '.' +Sta_req[i][j][2] + '.' + Sta_req[i][j][3]
                
                Exception_file = open(os.path.join(add_event[i], 'info', \
                    'exception'), 'a')

                ee = 'iris -- ' + dummy + '---' + str(i) + '-' + str(j) + '---' + \
                    Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
                    Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + \
                    '---' + str(e) + '\n'
                
                Exception_file.writelines(ee)
                Exception_file.close()
                print e 
        
        if input['iris_bulk'] == 'Y':
            if input['SAC'] == 'Y':
                for j in range(0, len_req_iris):
                    try:
                        writesac(address_st = os.path.join(add_event[i], 'BH_RAW', \
                            Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
                            Sta_req[i][j][2] + '.' + Sta_req[i][j][3]), \
                            sta_info = dic[j], ev_info = events[i])
                    except Exception, e:
                        pass
            input['waveform'] = 'Y'
        
        Report = open(os.path.join(add_event[i], 'info', 'report_st'), 'a')
        eventsID = events[i]['event_id']
        Report.writelines('<><><><><><><><><><><><><><><><><>' + '\n')
        Report.writelines(eventsID + '\n')
        Report.writelines('---------------IRIS---------------' + '\n')
        Report.writelines('---------------' + input['cha'] + '---------------' + '\n')
        rep = 'IRIS-Available stations for channel ' + input['cha'] + \
                ' and for event' + '-' + str(i) + ': ' + str(len(Sta_req[i])) + '\n'
        Report.writelines(rep)
        rep = 'IRIS-' + type + ' stations for channel ' + input['cha'] + \
                ' and for event' + '-' + str(i) + ':     ' + str(len(dic)) + '\n'
        Report.writelines(rep)
        Report.writelines('----------------------------------' + '\n')
            
        t_wave_2 = datetime.now()
        t_wave = t_wave_2 - t_wave_1
            
        rep = "Time for " + type + "ing Waveforms from IRIS: " + str(t_wave) + '\n'
        Report.writelines(rep)
        Report.writelines('----------------------------------' + '\n')
        Report.close()
    
    print "------------"
    print 'IRIS is DONE'
    print "------------"

###################### Arclink_network #############################

def ARC_network(input):
    
    """
    Returns information about what time series data is available 
    at the ArcLink nodes for all requested events
    """
        
    t_arc_1 = datetime.now()
    
    global events
    
    len_events = len(events)
    Period = input['min_date'].split('T')[0] + '_' + \
                input['max_date'].split('T')[0] + '_' + \
                str(input['min_mag']) + '_' + str(input['max_mag'])
    eventpath = os.path.join(input['datapath'], Period)
    
    if input['IRIS'] != 'Y':
        create_foders_files(events, eventpath)           
        
    print 'ArcLink-Folders are Created!'
    print "--------------------"
    
    Stas_arc = []
    
    for i in range(0, len_events):
    
        Sta_arc = ARC_available(input, events[i], eventpath, event_number = i)
        Stas_arc.append(Sta_arc)
        
        print 'ArcLink-Availability for event: ' + str(i+1) + str('/') + \
                                    str(len_events) + '  --->' + 'DONE'
        
        if input['get_continuous'] == 'Y':
            for j in range(1, len_events):
                Stas_arc.append(Sta_arc)
                print 'ArcLink-Availability for event: ' + str(j+1) + str('/') + \
                                    str(len_events) + '  --->' + 'DONE'
            break
        
    t_arc_2 = datetime.now()
    t_arc_21 = t_arc_2 - t_arc_1
    
    print "--------------------"
    print 'ARC-Time: (Availability)'
    print t_arc_21
    
    return Stas_arc

###################### ARC_available ###################################

def ARC_available(input, event, target_path, event_number):
    
    """
    Check the availablity of the IRIS stations
    """
    
    client_arclink = Client_arclink()
    Sta_arc = []
    
    try:
        
        inventories = client_arclink.getInventory(network=input['net'], \
            station=input['sta'], location=input['loc'], \
            channel=input['cha'], \
            starttime=UTCDateTime(event['datetime'])-10, \
            endtime=UTCDateTime(event['datetime'])+10, \
            instruments=False, route=True, sensortype='', \
            min_latitude=input['mlat_rbb'], max_latitude=input['Mlat_rbb'], \
            min_longitude=input['mlon_rbb'], max_longitude=input['Mlon_rbb'], \
            restricted=False, permanent=None, modified_after=None)
        
        for j in inventories.keys():
            netsta = j.split('.') 
            if len(netsta) == 4:
                sta = netsta[0] + '.' + netsta[1]
                if inventories[sta]['depth'] == None:
                    inventories[sta]['depth'] = 0
                Sta_arc.append([netsta[0], netsta[1], netsta[2], netsta[3],\
                        inventories[sta]['latitude'], inventories[sta]['longitude'],\
                        inventories[sta]['elevation'], inventories[sta]['depth']])      
        
        Sta_arc.sort()
        
    except Exception, e:
            
        Exception_file = open(os.path.join(target_path, \
            'info', 'exception'), 'a')
        ee = 'arclink -- Event:' + str(event_number) + '---' + str(e) + '\n'
        
        Exception_file.writelines(ee)
        Exception_file.close()
        print e

    return Sta_arc

###################### Arclink_waveform ############################

def ARC_waveform(input, Sta_req, type):
    
    """
    Gets Waveforms, Response files and meta-data 
    from ArcLink based on the requested events...
    """
    
    t_wave_1 = datetime.now()
    
    global events
    
    client_arclink = Client_arclink()
    add_event = []
    
    if type == 'save':
        Period = input['min_date'].split('T')[0] + '_' + \
                    input['max_date'].split('T')[0] + '_' + \
                    str(input['min_mag']) + '_' + str(input['max_mag'])
        eventpath = os.path.join(input['datapath'], Period)
        for i in range(0, len(events)):
            add_event.append(os.path.join(eventpath, \
                                        events[i]['event_id']))  
    elif type == 'update':
        events, add_event = quake_info(input['arc_update'], target = 'info')
    
    len_events = len(events)
    
    for i in range(0, len_events):
        print "--------------------"
        if input['test'] == 'Y':
            len_req_arc = input['test_num']
            
        else:    
            len_req_arc = len(Sta_req[i])       

        dic = {}
            
        for j in range(0, len_req_arc):
        
            print '------------------'
            print type
            print 'ArcLink-Event and Station Numbers are:'
            print str(i+1) + '/' + str(len_events) + '-' + str(j+1) + '/' + \
                    str(len(Sta_req[i])) + '-' + input['cha']
            
            try:
                
                client_arclink = Client_arclink(timeout=5)
                
                t11 = datetime.now()
                           
                                
                if input['waveform'] == 'Y':
                    
                    dummy = 'Waveform'
                
                    client_arclink.saveWaveform(os.path.join(add_event[i], \
                        'BH_RAW', \
                        Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3]), \
                        Sta_req[i][j][0], Sta_req[i][j][1], \
                        Sta_req[i][j][2], Sta_req[i][j][3], \
                        events[i]['t1'], events[i]['t2'])
                
                    print "Saving Waveform for: " + Sta_req[i][j][0] + \
                        '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + "  ---> DONE"  
                
                
                if input['response'] == 'Y':
                        
                    dummy = 'Response'
                    
                    client_arclink.saveResponse(os.path.join(add_event[i], \
                        'Resp', 'RESP' + \
                        '.' + Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3]), \
                        Sta_req[i][j][0], Sta_req[i][j][1], \
                        Sta_req[i][j][2], Sta_req[i][j][3], \
                        events[i]['t1'], events[i]['t2'])
                    
                    sp = Parser(os.path.join(add_event[i], \
                        'Resp', 'RESP' + '.' + Sta_req[i][j][0] + \
                        '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3]))
                    
                    sp.writeRESP(os.path.join(add_event[i], 'Resp'))
                    
                    print "Saving Response for: " + Sta_req[i][j][0] + \
                        '.' + Sta_req[i][j][1] + '.' + \
                        Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + "  ---> DONE"
                
                
                dummy = 'Meta-data'
                
                dic[j] ={'info': Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + \
                    '.' + Sta_req[i][j][2] + '.' + Sta_req[i][j][3], \
                    'net': Sta_req[i][j][0], 'sta': Sta_req[i][j][1], \
                    'latitude': Sta_req[i][j][4], 'longitude': Sta_req[i][j][5], \
                    'loc': Sta_req[i][j][2], 'cha': Sta_req[i][j][3], \
                    'elevation': Sta_req[i][j][6], 'depth': Sta_req[i][j][7]}
                
                Syn_file = open(os.path.join(add_event[i], \
                                    'info', 'station_event'), 'a')
                syn = Sta_req[i][j][0] + ',' + Sta_req[i][j][1] + ',' + \
                    Sta_req[i][j][2] + ',' + Sta_req[i][j][3] + ',' + \
                    str(Sta_req[i][j][4]) + ',' + str(Sta_req[i][j][5]) + \
                    ',' + str(Sta_req[i][j][6]) + ',' + \
                    str(Sta_req[i][j][7]) + ',' + events[i]['event_id'] + \
                    ',' + str(events[i]['latitude']) \
                     + ',' + str(events[i]['longitude']) + ',' + \
                     str(events[i]['depth']) + ',' + \
                     str(events[i]['magnitude']) + ',' + 'arc' + ',' + '\n'
                Syn_file.writelines(syn)
                Syn_file.close()
                
                if input['SAC'] == 'Y':
                    writesac(address_st = os.path.join(add_event[i], 'BH_RAW', \
                            Sta_req[i][j][0] +  '.' + Sta_req[i][j][1] + \
                            '.' + Sta_req[i][j][2] + '.' + Sta_req[i][j][3]), \
                            sta_info = dic[j], ev_info = events[i])
                
                print "Saving Station  for: " + Sta_req[i][j][0] + '.' + \
                    Sta_req[i][j][1] + '.' + \
                    Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + "  ---> DONE"
                
                
                t22 = datetime.now()
                    
                if input['time_arc'] == 'Y':
                    time_arc = t22 - t11
                    time_file = open(os.path.join(add_event[i], \
                                    'info', 'arc_time'), 'a')
                    size = getFolderSize(os.path.join(add_event[i]))
                    print size/1.e6
                    ti = Sta_req[i][j][0] + ',' + Sta_req[i][j][1] + ',' + \
                        Sta_req[i][j][2] + ',' + Sta_req[i][j][3] + ',' + \
                        str(time_arc.seconds) + ',' + \
                        str(time_arc.microseconds) + ',' + str(size/1.e6) + ',' + '\n'
                    time_file.writelines(ti)
                    time_file.close()
                
            except Exception, e:    
                                
            
                t22 = datetime.now()
                
                if input['time_arc'] == 'Y':
                    time_arc = t22 - t11
                    time_file = open(os.path.join(add_event[i], \
                                    'info', 'arc_time'), 'a')
                    size = getFolderSize(os.path.join(add_event[i]))
                    print size/1.e6
                    ti = Sta_req[i][j][0] + ',' + Sta_req[i][j][1] + ',' + \
                        Sta_req[i][j][2] + ',' + Sta_req[i][j][3] + ',' + \
                        str(time_arc.seconds) + ',' + \
                        str(time_arc.microseconds) + ',' + str(size/1.e6) + ',' + '\n'
                    time_file.writelines(ti)
                    time_file.close()
            
                
                print dummy + '---' + Sta_req[i][j][0] +    '.' + Sta_req[i][j][1] + \
                    '.' +Sta_req[i][j][2] + '.' + Sta_req[i][j][3]
                
                Exception_file = open(os.path.join(add_event[i], \
                                'info', 'exception'), 'a')

                ee = 'arclink -- ' + dummy + '---' + str(i) + '-' + str(j) + '---' + \
                    Sta_req[i][j][0] + '.' + Sta_req[i][j][1] + '.' + \
                    Sta_req[i][j][2] + '.' + Sta_req[i][j][3] + \
                    '---' + str(e) + '\n'
                
                Exception_file.writelines(ee)
                Exception_file.close()
                print e
                            
        
        Report = open(os.path.join(add_event[i], 'info', 'report_st'), 'a')
        eventsID = events[i]['event_id']
        Report.writelines('<><><><><><><><><><><><><><><><><>' + '\n')
        Report.writelines(eventsID + '\n')
        Report.writelines('---------------ARC---------------' + '\n')
        Report.writelines('---------------' + input['cha'] + '---------------' + '\n')
        rep = 'ARC-Available stations for channel ' + input['cha'] + \
                    ' and for event' + '-' + str(i) + ': ' + str(len(Sta_req[i])) + '\n'
        Report.writelines(rep)
        rep = 'ARC-' + type + ' stations for channel ' + \
                input['cha'] + ' and for event' + '-' + str(i) + ':     ' + str(len(dic)) + '\n'
        Report.writelines(rep)
        Report.writelines('----------------------------------' + '\n')
        
        t_wave_2 = datetime.now()
        t_wave = t_wave_2 - t_wave_1
        
        rep = "Time for " + type + "ing Waveforms from ArcLink: " + str(t_wave) + '\n'
        Report.writelines(rep)
        Report.writelines('----------------------------------' + '\n')
        Report.close()

    print "---------------"
    print 'ArcLink is DONE'
    print "---------------"

###################### IRIS_update #####################################
    
def IRIS_update(input, address):
    
    """
    Initialize folders and required stations for IRIS update requests
    """
    
    t_update_1 = datetime.now()
    
    client_iris = Client_iris()
    
    events, address_events = quake_info(address, 'info')
    len_events = len(events)
    
    Stas_iris = []
    
    for i in range(0, len_events):
    
        target_path = address_events
        Sta_iris = IRIS_available(input, events[i], target_path[i], event_number = i)
        Stas_iris.append(Sta_iris)
        
        if input['iris_bulk'] != 'Y':
            print 'IRIS-Availability for event: ' + str(i+1) + str('/') + \
                                    str(len_events) + '  ---> ' + 'DONE'
        else:
            print 'IRIS-bulkfile for event    : ' + str(i+1) + str('/') + \
                                    str(len_events) + '  ---> ' + 'DONE'
        
        if input['get_continuous'] == 'Y':
            for j in range(1, len_events):
                Stas_iris.append(Sta_iris)
                print 'IRIS-Availability for event: ' + str(j+1) + str('/') + \
                                    str(len_events) + '  --->' + 'DONE'
            break
    
    
    Stas_req = []
    
    for k in range(0, len_events):
        Sta_all = Stas_iris[k]
        Stas_req.append(rm_duplicate(Sta_all, \
                            address = os.path.join(address_events[k])))
            
    return Stas_req

###################### ARC_update ######################################
    
def ARC_update(input, address):
    
    """
    Initialize folders and required stations for ARC update requests
    """
    
    t_update_1 = datetime.now()
    
    client_arclink = Client_arclink()
    
    events, address_events = quake_info(address, 'info')
    len_events = len(events)
    
    Stas_arc = []
    
    for i in range(0, len_events):
        
        target_path = address_events
        Sta_arc = ARC_available(input, events[i], target_path[i], event_number = i)
        Stas_arc.append(Sta_arc)
        
        print 'ArcLink-Availability for event: ' + str(i+1) + str('/') + \
                                    str(len_events) + '  --->' + 'DONE'
        
        if input['get_continuous'] == 'Y':
            for j in range(1, len_events):
                Stas_arc.append(Sta_arc)
                print 'ArcLink-Availability for event: ' + str(j+1) + str('/') + \
                                    str(len_events) + '  --->' + 'DONE'
            break
        
    Stas_req = []
    
    for k in range(0, len_events):
        Sta_all = Stas_arc[k]
        Stas_req.append(rm_duplicate(Sta_all, \
                            address = os.path.join(address_events[k])))
            
    return Stas_req
    
###################### IRIS_ARC_IC #####################################

def IRIS_ARC_IC(input, clients):
    
    """
    Call "inst_correct" function based on the channel request.
    """
    
    if input[clients + '_ic_auto'] == 'Y':
        global events        
        Period = input['min_date'].split('T')[0] + '_' + \
                    input['max_date'].split('T')[0] + '_' + \
                    str(input['min_mag']) + '_' + str(input['max_mag'])
        eventpath = os.path.join(input['datapath'], Period)
        address = eventpath
    elif input[clients + '_ic'] != 'N':
        address = input[clients + '_ic']
    
    events, address_events = quake_info(address, 'info')
    
    for i in range(0, len(events)):
        sta_ev = read_station_event(address_events[i])
        ls_saved_stas = []
        
        for j in range(0, len(sta_ev[0])):
            if clients == sta_ev[0][j][13]:
                station_id = sta_ev[0][j][0] + '.' + sta_ev[0][j][1] + '.' + \
                             sta_ev[0][j][2] + '.' + sta_ev[0][j][3]
                ls_saved_stas.append(os.path.join(address_events[i], 'BH_RAW',\
                                        station_id))
        
        print 'event: ' + str(i+1) + '/' + str(len(events)) + \
                                                        ' -- ' + clients
        print '------------------------------------'
        inst_correct(input, ls_saved_stas, address_events[i], clients) 
        
    print "**********************************"
    print clients.upper() + ' Instrument Correction is DONE'
    print "**********************************"

###################### inst_correct ###############################
    
def inst_correct(input, ls_saved_stas, address, clients):
    
    """
    Apply Instrument Coorection on all available stations in the folder
    This scrips uses 'seisSim' from obspy.signal for this reason
    
    Instrument Correction has three main steps:
        1) RTR: remove the trend
        2) tapering
        3) pre-filtering and deconvolution of Resp file from Raw counts
    """
    
    t_inst_1 = datetime.now()
    
    if input['corr_unit'] == 'DIS':
        BH_file = 'BH'
    else:
        BH_file = 'BH_' + input['corr_unit']
    
    try:
        os.makedirs(os.path.join(address, BH_file))
    except Exception, e:
        pass
    
    for i in range(0, len(ls_saved_stas)):
        
        inform = clients + ' -- ' + str(i+1) + '/' + str(len(ls_saved_stas))
        
        # Removing the trend
        rt_c = RTR(stream = ls_saved_stas[i], degree = 2)
        tr = read(ls_saved_stas[i])[0]
        tr.data = rt_c
        
        # Tapering
        taper = invsim.cosTaper(len(tr.data))
        tr.data *= taper
        
        resp_file = os.path.join(address, 'Resp', 'RESP' + '.' + \
                                    ls_saved_stas[0].split('/')[-1])
        
        obspy_fullresp(trace = tr, resp_file = resp_file, \
            Address = os.path.join(address, BH_file), unit = input['corr_unit'], \
            BP_filter = input['pre_filt'], inform = inform)


    # ---------Creating Tar files (Response files)
    if input['zip_w'] == 'Y':
                        
        print '*********************'
        print 'Compressing Raw files'
        print '*********************'
            
        path = os.path.join(address, BH_RAW)
        tar_file = os.path.join(path, 'BH_RAW.tar')
        files = '*.*.*'
        
        compress_gzip(path = path, tar_file = tar_file, files = files)
                
    # ---------Creating Tar files (Response files)
    if input['zip_r'] == 'Y':
                
        print '**************************'
        print 'Compressing Response files'
        print '**************************'
        
        path = os.path.join(address, Resp)
        tar_file = os.path.join(path, 'Resp.tar')
        files = 'RESP.*'
        
        compress_gzip(path = path, tar_file = tar_file, files = files)
        
    
    t_inst_2 = datetime.now()
    
    print '-----------------------------------------------'
    print 'Time for Instrument Correction of ' + \
                    str(len(ls_saved_stas)) + ' stations:'
    print t_inst_2 - t_inst_1
    print '-----------------------------------------------'

###################### RTR #############################################

def RTR(stream, degree = 2):
    
    """
    Remove the trend by Fitting a linear function to the trace 
    with least squares and subtracting it
    """
    
    raw_f = read(stream)

    t = []
    b0 = 0
    inc = []
    
    b = raw_f[0].stats['starttime']

    for i in range(0, raw_f[0].stats['npts']):
        inc.append(b0)
        b0 = b0+1.0/raw_f[0].stats['sampling_rate'] 
        b0 = round(b0, 4)
        
    A = np.vander(inc, degree)
    (coeffs, residuals, rank, sing_vals) = np.linalg.lstsq(A, raw_f[0].data)
    
    f = np.poly1d(coeffs)
    y_est = f(inc)
    rt_c = raw_f[0].data-y_est
    
    return rt_c

###################### obspy_fullresp #######################################

def obspy_fullresp(trace, resp_file, Address, unit = 'DIS', \
            BP_filter = (0.008, 0.012, 3.0, 4.0), inform = 'N/N'):

    date = trace.stats['starttime']
    seedresp = {'filename':resp_file,'date':date,'units':unit}
    
    try:
        
        trace.data = seisSim(data = trace.data, \
            samp_rate = trace.stats.sampling_rate,paz_remove=None, \
            paz_simulate = None, remove_sensitivity=False, \
            simulate_sensitivity = False, water_level = 600.0, \
            zero_mean = True, taper = False, pre_filt=eval(BP_filter), \
            seedresp=seedresp, pitsasim=False, sacsim = True)
        
        trace_identity = trace.stats['station'] + '.' + \
                trace.stats['location'] + '.' + trace.stats['channel']
        trace.write(os.path.join(Address, unit.lower() + '.' + \
                                        trace_identity), format = 'SAC')

        print inform + ' -- Instrument Correction for: ' + trace_identity
        
    except Exception, e:
        print inform + ' -- ' + str(e)
        
###################### IRIS_ARC_merge ##################################

def IRIS_ARC_merge(input, clients):
    
    """
    Call "merge_stream" function
    """

    if input[clients + '_merge_auto'] == 'Y':
        global events        
        Period = input['min_date'].split('T')[0] + '_' + \
                    input['max_date'].split('T')[0] + '_' + \
                    str(input['min_mag']) + '_' + str(input['max_mag'])
        eventpath = os.path.join(input['datapath'], Period)
        address = eventpath
    elif input[clients + '_merge'] != 'N':
        address = input[clients + '_merge']
        
    events, address_events = quake_info(address, 'info')
    
    ls_saved_stas = []
    for i in range(0, len(events)):
        sta_ev = read_station_event(address_events[i])
        for j in range(0, len(sta_ev[0])):
            if clients == sta_ev[0][j][13]:
                
                if input['merge_folder'] == 'raw':
                    BH_file = 'BH_RAW'
                    network = sta_ev[0][j][0]
                elif input['merge_folder'] == 'corrected':
                    if input['corr_unit'] == 'DIS':
                        BH_file = 'BH'
                        network = 'dis'
                    elif input['corr_unit'] == 'VEL':
                        BH_file = 'BH_' + input['corr_unit']
                        network = 'vel'
                    elif input['corr_unit'] == 'ACC':
                        BH_file = 'BH_' + input['corr_unit']
                        network = 'acc'
                        
                station_id = network + '.' + sta_ev[0][j][1] + '.' + \
                             sta_ev[0][j][2] + '.' + sta_ev[0][j][3]
                ls_saved_stas.append(os.path.join(address_events[i], BH_file,\
                                        station_id))
    
    ls_saved_stations = []
    ls_address = []
    for i in range(0, len(ls_saved_stas)):
        ls_saved_stations.append(ls_saved_stas[i].split('/')[-1])
    ls_sta = list(set(ls_saved_stations))
    for i in range(0, len(address_events)):
        ls_address.append(os.path.join(address_events[i], BH_file))
    
    print '------------------------------------'
    merge_stream(ls_address = ls_address, ls_sta = ls_sta)

    print 'DONE'
    print '*****************************'

###################### merge_stream ####################################

def merge_stream(ls_address, ls_sta):
    
    global input
    
    address = os.path.dirname(os.path.dirname(ls_address[0]))
    try:
        os.makedirs(os.path.join(address, 'MERGED'))
    except Exception, e:
        pass
    
    for i in range(0, len(ls_sta)):
        for j in range(0, len(ls_address)):
            if os.path.isfile(os.path.join(ls_address[j], ls_sta[i])):
                st = read(os.path.join(ls_address[j], ls_sta[i]))
                for k in range(j+1, len(ls_address)):
                    try:
                        st.append(read(os.path.join(ls_address[k], \
                                                        ls_sta[i]))[0])
                    except Exception, e:
                        print e

                st.merge(method=1, fill_value='latest', interpolation_samples=0)
                trace = st[0]
                trace_identity = trace.stats['network'] + '.' + \
                        trace.stats['station'] + '.' + \
                        trace.stats['location'] + '.' + trace.stats['channel']
                st.write(os.path.join(address, 'MERGED', trace_identity), \
                                                        format = 'SAC')     
                break

###################### PLOT ############################################

def PLOT(input, clients):
    
    """
    Plotting tools
    """
    
    for i in ['plot_se', 'plot_sta', 'plot_ev', 'plot_ray', 'plot_epi']:
        if input[i] != 'N':
            events, address_events = quake_info(input[i], 'info')
    
    ls_saved_stas = []
    ls_add_stas = []
    
    for i in range(0, len(events)):
        
        ls_saved_stas_tmp = []
        ls_add_stas_tmp = []
        sta_ev = read_station_event(address_events[i])
        
        for j in range(0, len(sta_ev[0])):
            
            if input['plot_folder'] == 'raw':
                BH_file = 'BH_RAW'
                network = sta_ev[0][j][0]
            elif input['plot_folder'] == 'corrected':
                if input['corr_unit'] == 'DIS':
                    BH_file = 'BH'
                    network = 'dis'
                elif input['corr_unit'] == 'VEL':
                    BH_file = 'BH_' + input['corr_unit']
                    network = 'vel'
                elif input['corr_unit'] == 'ACC':
                    BH_file = 'BH_' + input['corr_unit']
                    network = 'acc'
                    
            station_id = network + ',' + sta_ev[0][j][1] + ',' + \
                         sta_ev[0][j][2] + ',' + sta_ev[0][j][3] + ',' + \
                         sta_ev[0][j][4] + ',' + sta_ev[0][j][5] + ',' + \
                         sta_ev[0][j][6] + ',' + sta_ev[0][j][7] + ',' + \
                         sta_ev[0][j][8] + ',' + sta_ev[0][j][9] + ',' + \
                         sta_ev[0][j][10] + ',' + sta_ev[0][j][11] + ',' + \
                         sta_ev[0][j][12] + ',' + sta_ev[0][j][13]

            if input['plot_all'] != 'Y':
                if clients == sta_ev[0][j][13]:
                    ls_saved_stas_tmp.append(station_id)
                    ls_add_stas_tmp.append(os.path.join(address_events[i], \
                                            BH_file, network + '.' + \
                                            sta_ev[0][j][1] + '.' + \
                                            sta_ev[0][j][2] + '.' + \
                                            sta_ev[0][j][3]))
            elif input['plot_all'] == 'Y':
                ls_saved_stas_tmp.append(station_id)
                ls_add_stas_tmp.append(os.path.join(address_events[i], \
                                            BH_file, network + '.' + \
                                            sta_ev[0][j][1] + '.' + \
                                            sta_ev[0][j][2] + '.' + \
                                            sta_ev[0][j][3]))
        
        ls_saved_stas.append(ls_saved_stas_tmp)
        ls_add_stas.append(ls_add_stas_tmp)
    
    for i in range(0, len(ls_saved_stas)):
        for j in range(0, len(ls_saved_stas[i])):
            ls_saved_stas[i][j] = ls_saved_stas[i][j].split(',')
    
    for i in ['plot_se', 'plot_sta', 'plot_ev', 'plot_ray']:
        if input[i] != 'N':
            plot_se_ray(input, ls_saved_stas)
    
    if input['plot_epi']:
        plot_epi(input, ls_add_stas, ls_saved_stas)
    
###################### plot_se_ray #####################################

def plot_se_ray(input, ls_saved_stas):
    
    """
    Plot: station, event, both and ray path
    """

    plt.clf()

    m = Basemap(projection='aeqd', lon_0=-100, lat_0=40, \
                                                resolution='c')

    m.drawcoastlines()
    #m.fillcontinents()
    m.drawparallels(np.arange(-90.,120.,30.))
    m.drawmeridians(np.arange(0.,420.,60.))
    m.drawmapboundary()
        
    for i in range(0, len(ls_saved_stas)):
        print str(i + 1) + '/' + str(len(ls_saved_stas))
        print '---------'
        
        if input['plot_se'] != 'N' or \
                            input['plot_ev'] != 'N' or \
                            input['plot_ray'] != 'N':   
            x_ev, y_ev = m(float(ls_saved_stas[i][0][10]), \
                           float(ls_saved_stas[i][0][9]))
            m.scatter(x_ev, y_ev, \
                        math.log(float(ls_saved_stas[i][0][12])) ** 6, \
                        color="red", marker="o", \
                        edgecolor="black", zorder=10)
        
        for j in range(0, len(ls_saved_stas[i])):
            try:           
                
                st_lat = float(ls_saved_stas[i][j][4])
                st_lon = float(ls_saved_stas[i][j][5])
                ev_lat = float(ls_saved_stas[i][j][9])
                ev_lon = float(ls_saved_stas[i][j][10])
                ev_mag = float(ls_saved_stas[i][j][12])

                if input['plot_ray'] != 'N':
                    m.drawgreatcircle(ev_lon, ev_lat, st_lon, st_lat, \
                                    alpha = 0.1)
                        
                if input['plot_se'] != 'N' or \
                                input['plot_sta'] != 'N' or \
                                input['plot_ray'] != 'N':
                    
                    x_sta, y_sta = m(st_lon, st_lat)
                    m.scatter(x_sta, y_sta, 20, color='blue', marker="o", \
                                            edgecolor="black", zorder=10)
            
            except Exception, e:
                print e
                pass
                
    print 'Saving the plot in the following address:'
    print input['plot_save'] + 'plot.' + input['plot_format']
    
    plt.savefig(os.path.join(input['plot_save'], 'plot.' + \
                                                input['plot_format']))

###################### plot_epi ########################################

def plot_epi(input, ls_add_stas, ls_saved_stas):
    
    """
    Plot: Epicentral distance-Time
    """
            
    plt.clf()
    
    for target in range(0, len(ls_add_stas)):
        print str(target + 1) + '/' + str(len(ls_add_stas))
        print '---------'
        
        for i in range(0, len(ls_add_stas[target])):
            
            try:
                
                tr = read(ls_add_stas[target][i])[0]
                tr.normalize()
                dist = locations2degrees(float(ls_saved_stas[target][i][9]), \
                            float(ls_saved_stas[target][i][10]), \
                            float(ls_saved_stas[target][i][4]), \
                            float(ls_saved_stas[target][i][5]))
                if input['min_epi'] <= dist <= input['max_epi']:
                    x = range(0, len(tr.data))
                    for i in range(0, len(x)):
                        x[i] = x[i]/float(tr.stats['sampling_rate'])
                    plt.plot(x, tr.data + dist, color = 'black')
            
            except Exception, e:
                print e
                pass
            
            plt.xlabel('Time (sec)')
            plt.ylabel('Epicentral distance (deg)')

    print 'Saving the plot in the following address:'
    print input['plot_save'] + 'plot.' + input['plot_format']
    
    plt.savefig(os.path.join(input['plot_save'], 'plot.' + \
                                                input['plot_format']))

###################### XML_list_avail ##################################

def XML_list_avail(xmlfile):
    
    """
    This module changes the XML file got from availability to a list
    """
    
    sta_obj = objectify.XML(xmlfile)
    sta_req = []

    for i in range(0, len(sta_obj.Station)):
        
        station = sta_obj.Station[i]
        net = station.get('net_code')
        sta = station.get('sta_code')
        
        lat = str(station.Lat)
        lon = str(station.Lon)
        ele = str(station.Elevation)
        
        for j in range(0, len(station.Channel)):
            cha = station.Channel[j].get('chan_code')
            loc = station.Channel[j].get('loc_code')
            
            sta_req.append([net, sta, loc, cha, lat, lon, ele])
    
    return sta_req

###################### create_foders_files #############################

def create_foders_files(events, eventpath):
    
    """
    Create required folders and files in the event folder(s)
    """
    
    len_events = len(events)
    
    for i in range(0, len_events):
        if os.path.exists(os.path.join(eventpath, events[i]['event_id'])) == True:
            
            if raw_input('Folder for -- the requested Period (min/max) ' + \
            'and Magnitude (min/max) -- exists in your directory.' + '\n\n' + \
            'You could either close the program and try updating your ' + \
            'folder OR remove the tree, continue the program and download again.' + \
            '\n' + 'Do you want to continue? (Y/N)' + '\n') == 'Y':
                print '-------------------------------------------------------------'
                shutil.rmtree(os.path.join(eventpath, events[i]['event_id']))
            
            else:
                print '------------------------------------------------'
                print 'So...you decided to update your folder...Ciao'
                print '------------------------------------------------'
                sys.exit()

    for i in range(0, len_events):
        try:
            os.makedirs(os.path.join(eventpath, events[i]['event_id'], 'BH_RAW'))
            os.makedirs(os.path.join(eventpath, events[i]['event_id'], 'Resp'))
            os.makedirs(os.path.join(eventpath, events[i]['event_id'], 'info'))
        except Exception, e:
            pass
    
    for i in range(0, len_events):
        Report = open(os.path.join(eventpath, events[i]['event_id'], \
            'info', 'report_st'), 'a+')
        Report.close()
    
    
    for i in range(0, len_events):
        Exception_file = open(os.path.join(eventpath, events[i]['event_id'], \
            'info', 'exception'), 'a+')
        eventsID = events[i]['event_id']
        Exception_file.writelines('\n' + eventsID + '\n')
        
        Syn_file = open(os.path.join(eventpath, events[i]['event_id'], \
            'info', 'station_event'), 'a+')
        Syn_file.close()
        
    if input['time_iris'] == 'Y':
        for i in range(0, len_events):
            time_file = open(os.path.join(eventpath, events[i]['event_id'], \
                    'info', 'iris_time'), 'a+')
            time_file.close()
    
        
    for i in range(0, len_events):
        quake_file = open(os.path.join(eventpath, events[i]['event_id'],\
                            'info', 'quake'), 'a+')
        
        quake_file.writelines(repr(events[i]['datetime'].year).rjust(15)\
                + repr(events[i]['datetime'].julday).rjust(15) \
                + repr(events[i]['datetime'].month).rjust(15) \
                + repr(events[i]['datetime'].day).rjust(15) + '\n')
        quake_file.writelines(repr(events[i]['datetime'].hour).rjust(15)\
                + repr(events[i]['datetime'].minute).rjust(15) + \
                repr(events[i]['datetime'].second).rjust(15) + \
                repr(800).rjust(15) + '\n')
        
        quake_file.writelines(\
                ' '*(15 - len('%.5f' % events[i]['latitude'])) + '%.5f' \
                % events[i]['latitude'] + \
                ' '*(15 - len('%.5f' % events[i]['longitude'])) + '%.5f' \
                % events[i]['longitude'] + '\n')
        quake_file.writelines(\
                ' '*(15 - len('%.5f' % abs(events[i]['depth']))) + '%.5f' \
                % abs(events[i]['depth']) + '\n')
        quake_file.writelines(\
                ' '*(15 - len('%.5f' % abs(events[i]['magnitude']))) + '%.5f' \
                % abs(events[i]['magnitude']) + '\n')
        quake_file.writelines(\
                ' '*(15 - len(events[i]['event_id'])) + \
                        events[i]['event_id'] + '-' + '\n')
        
        quake_file.writelines(repr(events[i]['t1'].year).rjust(15)\
                + repr(events[i]['t1'].julday).rjust(15) \
                + repr(events[i]['t1'].month).rjust(15) \
                + repr(events[i]['t1'].day).rjust(15) + '\n')
        quake_file.writelines(repr(events[i]['t1'].hour).rjust(15)\
                + repr(events[i]['t1'].minute).rjust(15) + \
                repr(events[i]['t1'].second).rjust(15) + \
                repr(800).rjust(15) + '\n')
        
        quake_file.writelines(repr(events[i]['t2'].year).rjust(15)\
                + repr(events[i]['t2'].julday).rjust(15) \
                + repr(events[i]['t2'].month).rjust(15) \
                + repr(events[i]['t2'].day).rjust(15) + '\n')
        quake_file.writelines(repr(events[i]['t2'].hour).rjust(15)\
                + repr(events[i]['t2'].minute).rjust(15) + \
                repr(events[i]['t2'].second).rjust(15) + \
                repr(800).rjust(15) + '\n')

###################### writesac ########################################

def writesac(address_st, sta_info, ev_info):
    
    st = read(address_st)
    st[0].write(address_st, 'SAC')
    st = read(address_st)
    
    if sta_info['latitude'] != None:
        st[0].stats['sac']['stla'] = sta_info['latitude']
    if sta_info['longitude'] != None:
        st[0].stats['sac']['stlo'] = sta_info['longitude']
    if sta_info['elevation'] != None:
        st[0].stats['sac']['stel'] = sta_info['elevation']
    if sta_info['depth'] != None:
        st[0].stats['sac']['stdp'] = sta_info['depth']
    
    if ev_info['latitude'] != None:
        st[0].stats['sac']['evla'] = ev_info['latitude']    
    if ev_info['longitude'] != None:
        st[0].stats['sac']['evlo'] = ev_info['longitude']   
    if ev_info['depth'] != None:
        st[0].stats['sac']['evdp'] = ev_info['depth']
    if ev_info['magnitude'] != None:
        st[0].stats['sac']['mag'] = ev_info['magnitude']
        
    st[0].write(address_st, 'SAC')

###################### rm_duplicate ####################################

def rm_duplicate(Sta_all, address):
    
    """
    remove duplicates and give back the required list for updating
    """
        
    sta_all = []
    saved = []
        
    for i in Sta_all:
        if i[2] == '--' or i[2] == '  ':
            i[2] = ''
        for j in range(0, len(i)):
            if i[j] != str(i[j]):
                i[j] = str(i[j]) 
        if len(i) == 7:
            sta_all.append(str(i[0] + '_' + i[1] + '_' + i[2] + '_' + \
                            i[3] + '_' + i[4] + '_' + i[5] + '_' + i[6]))
        elif len(i) == 8:
            sta_all.append(str(i[0] + '_' + i[1] + '_' + i[2] + '_' + \
                            i[3] + '_' + i[4] + '_' + i[5] + '_' + i[6]\
                             + '_' + i[7]))
                            
    sta_ev = read_station_event(address)
    ls_saved_stas = sta_ev[0]
    
    for i in range(0, len(ls_saved_stas)):
        sta_info = ls_saved_stas[i]
        saved.append(sta_info[0] + '_' + sta_info[1] + '_' + \
                            sta_info[2] + '_' + sta_info[3])
    
    Stas_req = sta_all
    
    len_all_sta = len(sta_all)
    num = []
    for i in range(0, len(saved)):
        for j in range(0, len(Stas_req)):
            if saved[i] in Stas_req[j]:
                num.append(j)

    num.sort(reverse=True)
    for i in num:
        del Stas_req[i]  
    
    for m in range(0, len(Stas_req)):
        Stas_req[m] = Stas_req[m].split('_')
    
    Stas_req.sort()
    
    print '------------------------------------------'
    print 'Info:'
    print 'Number of all saved stations:     ' + str(len(saved))
    print 'Number of all available stations: ' + str(len_all_sta)
    print 'Number of stations to update for: ' + str(len(Stas_req))
    print '------------------------------------------'
    
    return Stas_req

###################### read_station_event ##############################

def read_station_event(address):
    
    """
    Reads the station_event file ("info" folder)
    """
    
    if address.split('/')[-1].split('.') == ['info']:
        target_add = [address]
    elif locate(address, 'info'):
        target_add = locate(address, 'info')
    else:
        print 'Error: There is no "info" folder in the address.'
    
    sta_ev = []
    
    for k in range(0, len(target_add)):
        sta_ev_tmp = []
        sta_file_open = open(os.path.join(target_add[k],\
                                                'station_event'), 'r')
        sta_file = sta_file_open.readlines()
        for i in sta_file:
            sta_ev_tmp.append(i.split(','))
        sta_ev.append(sta_ev_tmp)
    
    return sta_ev

###################### quake_info ######################################

def quake_info(address, target):
    
    """
    Reads the info in quake file ("info" folder)
    """
    
    events = []
    target_add = locate(address, target)
    
    for k in range(0, len(target_add)):
        quake_file_open = open(os.path.join \
                                    (target_add[k], 'quake'), 'r')
        quake_file = quake_file_open.readlines()

        tmp = []
        
        for i in quake_file:
            for j in i.split():
                try:
                    tmp.append(float(j))
                except ValueError:
                    pass
        
        quake_d = {'year0': int(tmp[0]), 'julday0': int(tmp[1]), \
                'hour0': int(tmp[4]), 'minute0': int(tmp[5]), \
                'second0': int(tmp[6]), 'lat': float(tmp[8]), \
                'lon': float(tmp[9]), 'dp': float(tmp[10]), \
                'mag': float(tmp[11]), \
                'year1': int(tmp[12]), 'julday1': int(tmp[13]), \
                'hour1': int(tmp[16]), 'minute1': int(tmp[17]), \
                'second1': int(tmp[18]), \
                'year2': int(tmp[20]), 'julday2': int(tmp[21]), \
                'hour2': int(tmp[24]), 'minute2': int(tmp[25]), \
                'second2': int(tmp[26]),}
        
        quake_t0 = UTCDateTime(year=quake_d['year0'], julday=quake_d['julday0'], \
                        hour=quake_d['hour0'], minute=quake_d['minute0'], \
                        second=quake_d['second0'])
        quake_t1 = UTCDateTime(year=quake_d['year1'], julday=quake_d['julday1'], \
                        hour=quake_d['hour1'], minute=quake_d['minute1'], \
                        second=quake_d['second1'])
        quake_t2 = UTCDateTime(year=quake_d['year2'], julday=quake_d['julday2'], \
                        hour=quake_d['hour2'], minute=quake_d['minute2'], \
                        second=quake_d['second2'])
        
        events.append({'author': 'NONE', 'datetime': quake_t0,\
                    'depth': quake_d['dp'],
                    'event_id': quake_file[5].split('-')[0].lstrip(),
                    'flynn_region': 'NONE',
                    'latitude': quake_d['lat'],
                    'longitude': quake_d['lon'],
                    'magnitude': quake_d['mag'],
                    'magnitude_type': 'NONE',
                    'origin_id': -12345.0,
                    't1': quake_t1,
                    't2': quake_t2})

    address_event = []
    for i in range(0, len(target_add)):
        address_event.append(os.path.dirname(target_add[i]))
    
    return events, address_event
    
###################### compress_gzip ###################################

def compress_gzip(path, tar_file, files):
            
    tar = tarfile.open(tar_file, "w:gz")
    os.chdir(path)
    
    for infile in glob.glob( os.path.join(path, files) ):
        
        print '------------------------------------'
        print 'Compressing:'
        print infile
        
        tar.add(infile.split('/')[-1])
        os.remove(infile)
    
    tar.close()

###################### send_email ######################################

def send_email(input, t1_pro):
    
    """
    Sending email to "email_address" specified in INPUT.cfg with:
    subject: starting-time-day_starting-time-month_tty
    contains:   
    * hostname_tty
    * Period: min-datetime_max-datetime_min-magnitude_max-magnitude
    * starting-time-program_end-time-program
    * total-time
    """ 
    
    t2_pro = datetime.now()
    t_pro = t2_pro - t1_pro
    
    info = commands.getoutput('hostname') + '_' + commands.getoutput('tty')
    Period = input['min_date'].split('T')[0] + '_' + \
                input['max_date'].split('T')[0] + '_' + \
                str(input['min_mag']) + '_' + str(input['max_mag'])
    
    i1 = str(info)
    i2 = str(Period)
    i3 = str(t1_pro).split(' ')[0] + '_' + str(t1_pro).split(' ')[1]
    i4 = str(t2_pro).split(' ')[0] + '_' + str(t2_pro).split(' ')[1]
    i5 = str(t_pro)
    if len(i5.split(' ')) == 1:
        i5 = str(t_pro)
    if len(i5.split(' ')) == 3:
        i5 = i5.split(' ')[0] + '_' + i5.split(' ')[1][:-1] + '_' + i5.split(' ')[2]
    
    i6 = str(str(t1_pro.day) + '_' + \
                str(t1_pro.month) + '_' + commands.getoutput('tty'))
    i7 = input['email_address']
    
    commands.getoutput('./email-obspyDMT.sh' + ' ' + i1 + ' ' + i2 + \
                    ' ' + i3 + ' ' + i4 + ' ' + i5 + ' ' + i6 + ' ' + i7)

###################### report_DMT #######################################

def report_DMT(input):
    
    """
    Generating Report for the request.

    contains:   
    * report_iris.txt
    * report_arc.txt

    * excep_iris.txt
    * excep_arc.txt

    * DQ_iris.txt
    * DQ_arc.txt

    * TQ_iris.txt
    * TQ_arc.txt

    * gap_iris.txt
    * gap_arc.txt
    """ 

    i1 = input['datapath']
    i2 = os.path.join(input['datapath'], 'REPORT')

    if os.path.exists(i2) == True:
        shutil.rmtree(i2)
        os.makedirs(i2)
        
    else:
        os.makedirs(i2)
    
    commands.getoutput('./REPORT.tcsh' + ' ' + i1 + ' ' + i2)

###################### getFolderSize ###################################

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

###################### locate ##########################################

def locate(root = '.', target = 'info'):

    """
    Locates a subdirectory within a directory.
    """
    
    matches = []
    
    for root, dirnames, filenames in os.walk(root):
        for dirnames in fnmatch.filter(dirnames, target):
            matches.append(os.path.join(root, dirnames))
    
    return matches

########################################################################
########################################################################
########################################################################

if __name__ == "__main__":
    
    t1_pro = time.time()
    status = obspyDMT()
    
    try:
        global input, events
        size = getFolderSize(input['datapath'])
        size /= 1.e6
       
        t_pro = time.time() - t1_pro
        
        print "Following folder contains %f MB of data."  % (size)
        print input['datapath']
        print ''
        print "Total time for last request: %f seconds" % (t_pro)
        print "--------------------------------------------------"
        
       # -------------------------------------------------------------------
        Period = input['min_date'].split('T')[0] + '_' + \
                    input['max_date'].split('T')[0] + '_' + \
                    str(input['min_mag']) + '_' + str(input['max_mag'])
        eventpath = os.path.join(input['datapath'], Period)
                
        len_events = len(events)
        
        address = []
        for i in range(0, len_events):
            address.append(os.path.join(eventpath, events[i]['event_id']))
       # -------------------------------------------------------------------
        print "Address of the stored events:"
        for i in range(0, len_events):
            print address[i]
        print "--------------------------------------------------"
        
    except Exception, e:
        print e
        pass
    
    # pass the return of main to the command line.
    sys.exit(status)

