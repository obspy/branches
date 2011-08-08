#! /usr/bin/env python
# -*- coding: utf-8 -*-

#from distutils.core import setup
import distribute_setup
distribute_setup.use_setuptools()

from setuptools import find_packages, setup

#### some stuff from experimenting with py2exe
#import py2exe
#import matplotlib
#
#opts = {
#        "py2exe": {"packages": ["encodings"], 
#                   'excludes': ['_gtkagg','_agg2','_cairo','_gtk','PyQt4._qt'],
#                   'includes': ['obspy.mseed']
#                   }
#        }
#windows=['sm_gui.py'],
#data_files=matplotlib.get_py2exe_datafiles(),
#      options = opts

NAME = 'sm_analyser'
AUTHOR = 'Yannik Behr'
AUTHOR_EMAIL = 'yannik@yanmail.de'
INSTALL_REQUIRES = ['obspy.core','obspy.sac','matplotlib>0.9.0']
VERSION='0.1.0'


def setupPackage():
    # automatically install distribute if the user does not have it installed 
    setup(
          name=NAME,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          version=VERSION,
          install_requires=INSTALL_REQUIRES,
#          packages=['sm_analyser'],
          packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
          scripts=['sm_analyser/scripts/sm_gui.py']
          )
    
if __name__ == '__main__':
    setupPackage()
    