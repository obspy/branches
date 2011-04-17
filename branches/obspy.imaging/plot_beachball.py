#!/usr/bin/env python
# basic example from tutorial
from core import Beachball
#from obspy.imaging.beachball import Beachball

mt = [0.91, -0.89, -0.02, 1.78, -1.55, 0.47]
#Beachball(mt, size=200, linewidth=2, facecolor='b', width=1000)
Beachball(mt, size=200, linewidth=2, facecolor='b', nofill=True)
Beachball(mt, size=200, linewidth=2, facecolor='b', outfile="wrap", format="png", nofill=True)
