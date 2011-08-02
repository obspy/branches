from distutils.core import setup

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
INSTALL_REQUIRES = ['obspy(>0.4.0)']
VERSION='0.1.0'


def setupPackage():
    setup(
          name=NAME,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          version=VERSION,
          requires=INSTALL_REQUIRES,
          packages=['sm_analyser'],
          scripts=['sm_analyser/scripts/sm_gui.py']
          )
    
if __name__ == '__main__':
    setupPackage()
    