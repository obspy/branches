#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import ipdb; ipdb.set_trace()

"""
NDLB-Part_I (No Data Left Behind-Part_I)

Goal: Management, Instrument Correction and Plotting of Large Seismic Datasets based on "Process-centric" method

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
 (http://www.gnu.org/copyleft/lesser.html)
"""

"""
- Import required Modules (Python and Obspy)
- ObsPyDMT and ObsPyLoad
- Instrument Correction
- ObsPyPT
"""

# ------------------------Import required Modules (Python and Obspy)-------------
from datetime import datetime

from ObsPyDMT import *
#from obspyload import *
from ObsPyPT import *

####################################################################################################################################
########################################################### Main Program ###########################################################
####################################################################################################################################

def NDLB_part_I():
	
	t1_pro = datetime.now()

	print '--------------------------------------------------------------------------------'
	bold = "\033[1m"
	reset = "\033[0;0m"
	print '\t\t\t\t' + bold + 'NDLB_part_I' + reset + '\n\t\t\t' + '(' + bold + 'N' + reset + 'o ' + bold + 'D' + reset + 'ata ' + bold + 'L' + reset + 'eft ' + bold + 'B' + reset + 'ehind ' + bold + 'Part I' + reset + ')' + '\n'
	print bold + 'Goal' + reset + ': Automatic tool for Management, Instrument Correction and Plotting of' + '\n' + 'Large Seismic Datasets based on "Process-centric" method' + '\n'
	print ':copyright:'
	print 'The ObsPy Development Team (devs@obspy.org)' + '\n'
	print ':license:'
	print 'GNU Lesser General Public License, Version 3'
	print '(http://www.gnu.org/copyleft/lesser.html)'
	print '--------------------------------------------------------------------------------'
	print '--------------------------------------------------------------------------------' + '\n'
	
	user_input = raw_input('NDLB_part_I could do the following taske for you:' + '\n\n' + \
			'1. Save raw counts, response file, quality control (Gap, Timing Quality, Data Quality) and update the folder.' + '\n' +
			'2. Instrument Correction (Acceleration, Velocity or Displacement)' + '\n'
			'3. Plotting events, available stations and ray path.' + '\n\n' + 
			'Please choose what you want to do:')
	print '--------------------------------------------------------------------------------' + '\n'
	
	
	# ------------------------ ObsPyDMT and ObsPyLoad ------------------------
	if user_input == '1':
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
		print '1. Save raw counts, response file, quality control (Gap, Timing Quality, Data Quality) and update the folder.'
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>' + '\n'
		
		user_input_1 = raw_input('a. ObsPyDMT (ObsPy Data Management Tool) --> Download raw counts, response files and other information by reading the "INPUT" file.' + '\n' +
			'b. ObsPyLoad (ObsPy Seismic Data Downloader tool) --> an automated and cross-platform command line data download tool.' + '\n\n' +
			'Please choose one of the tools:')
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>' + '\n'

		if user_input_1 == 'a':
			ObsPyDMT()
	
		if user_input_1 == 'b':
			obspyload()
	
	# ------------------------ Instrument Correction ------------------------
	if user_input == '2':
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
		print '2. Instrument Correction (Acceleration, Velocity or Displacement)'
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>' + '\n'
		
		user_input_2 = raw_input('You could correct the seismogram/s to:' + '\n\n' + \
			'a. Acceleration' + '\n' +
			'b. Velocity' + '\n' +
			'c. Displacement' + '\n\n' +
			'Please choose one of them:')
		print 'Under Construction!!!'
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>' + '\n'
	
	# ------------------------ ObsPyPT ------------------------
	if user_input == '3':
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><>'
		print '3. Plotting events, available stations and ray path.'
		print '<><><><><><><><><><><><><><><><><><><><><><><><><><><>' + '\n'
		ObsPyPT()


if __name__ == "__main__":
	status = NDLB_part_I()
	sys.exit(status)
