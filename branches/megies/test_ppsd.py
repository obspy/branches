from obspy.signal.psd import PPSD
from obspy.core import *
from obspy.xseed import Parser

st = read("/tmp/BW.KW1..EHZ.D.2011.090")
tr = st[0]
p = Parser("/tmp/dataless.seed.BW_KW1")
paz = p.getPAZ("BW.KW1..EHZ")
ppsd = PPSD(tr.stats, paz)
#ppsd.add(tr)
#ppsd.add(st[1])
#ppsd.plot()
#ppsd.save("/tmp/ppsd")
