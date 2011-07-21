#!/usr/bin/env python
#------------------------------------------------------------------------------
# Filename: reftek_rescue.py
#  Purpose: Restore REFTEK data from formatted storage media
#   Author: Tobias Megies
#    Email: tobias.megies@geophysik.uni-muenchen.de
#
# Copyright (C) 2011 Tobias Megies
#------------------------------------------------------------------------------
"""
Restore REFTEK data from formatted storage media.

This program is intended for restoring REFTEK packets from dumped disk
images, e.g. from formatted but not yet overwritten storage media.
The raw dumped data is searched for a header pattern consisting of
experiment number, year and REFTEK DAS ID.
Currently every packet is written to an individual file which can lead to an
enormous amount of files.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import with_statement
import os
import mmap
import contextlib
from binascii import b2a_hex, a2b_hex

#= PARAMETERS =================================================================
# filename of disk dump image
file_dd = "/export/data/A03F.IMG"
experiment_number = "00" # two chars, usually "00" (?)
year = "11" # last two digits of year as string
reftek_id = "A03F" # four char REFTEK DAS ID
outfolder = "/export/data/rescue/all_daily_test/"
#==============================================================================


# The REFTEK documentation defines other packets too, but these seem to be the
# only ones appearing in normal acquisition.
# see http://support.reftek.com/support/130-01/doc/130_record.pdf
PACKET_TYPES = ('DT', 'EH', 'ET')
# The longer the search patterns, the safer the identification of a packet
# header starting point. The search could probably be improved using the
# regular expressions module.
pattern = experiment_number + year + reftek_id
pattern = a2b_hex(pattern)

# memory map the file
with open(file_dd, 'r') as f:
    fno = f.fileno()
    access = mmap.ACCESS_READ
    with contextlib.closing(mmap.mmap(fno, 0, access=access)) as m:

        # pos marks the current position for the pattern search
        # (searched pattern starts 2 bytes after packet start)
        pos = m.find(pattern, 2)
        # abort when no new occurrence of pattern is found
        while pos > -1:
            # ind marks the actual packet start 2 bytes left of pos
            ind = pos - 2
            # if it seems we have found a packet, process it
            if m[ind:ind+2] in PACKET_TYPES:
                # all packet types have the same 16 byte header
                header = m[ind:ind+16]
                # from byte 3 onward information is stored in packed BCD format
                header = header[:2] + b2a_hex(header[2:])
                header = header.upper()
                # all packets consist of 1024 bytes
                packet = m[ind:ind+1024]
                # write to outfolder with header representation as filename
                filename = os.path.join(outfolder, header)
                # mark as *possibly* corrupted if a packet type string is found
                # inside the packet again.
                if any([pt in packet[1:] for pt in PACKET_TYPES]):
                    filename += "X"
                if pattern in packet[3:]:
                    filename += "XX"
                open(filename, "wb").write(packet)
            # search for pattern in memory map starting right of last position
            pos = m.find(pattern, pos + 1)
