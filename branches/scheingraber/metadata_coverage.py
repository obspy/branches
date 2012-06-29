#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to obtain statistics of the coverage of available metadata for a given
download project.
"""

import os
import glob

# INPUT
datapath = 'obspyload-data'
metadatapath = 'obspyload-metadata'

##########################################################

# create a dictionary of all stations that were downloaded
available = {}

# go through MiniSEED data
listing = os.listdir(datapath)
for indir in listing:
    thisdir = os.path.join(datapath, indir)
    if os.path.isdir(thisdir):
        for infile in glob.glob(os.path.join(thisdir, '*.mseed')):
            identifier = infile.split('/')[2][:-6]
            # create entry for identifier if not existing
            available.setdefault(identifier, {'data':True, 'metadata':False})


# go through RESP files
for infile in glob.glob(os.path.join(metadatapath, 'RESP.*')):
    identifier = infile.split('/')[1][5:]
    # create entry for identifier if not existing
    available.setdefault(identifier, {'data': False, 'metadata': True})
    # set again to true, for the case this existed before
    available[identifier]['metadata'] = True

# create statistics: how many percent of retrieved stations is covered
uncovered = [] # holds identifiers of uncovered data
covered = 0
total = 0
for identifier, available in available.items():
    if available['data']:
        total += 1
        if available['metadata']:
            covered += 1
        else:
            # add to uncovered data list
            uncovered.append(identifier)

uncovered.sort()
print "\nUncovered stations:"
print "==================="
print uncovered

print "\n%.2f%% of the data is covered with metadata." % (100.0*covered/total)
