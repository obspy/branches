# -*- coding: utf-8 -*-

"""
Unit tests for Volume1/Volume2 reader.
"""

import numpy as np
import os
import unittest
import sys
# make sure local copy is tested
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from sm_analyser.read_gns_sm_data import Vol12Reader

class GNSSmTestCase(unittest.TestCase):

    def setUp(self):
        # Directory where the test files are located
        self.path = os.path.dirname(__file__)
    
    def test_Vol1Reader(self):
        testfile = os.path.join(self.path, 'data', '20110613_022049_CACS.v1a')
        v1 = Vol12Reader(testfile,headonly=False)
        self.assertEqual(v1.stream[0].stats.npts,29000)
        self.assertEqual(v1.stream[0].data.size,29000)
        self.assertEqual(v1.stream[1].stats.sampling_rate,200.0)
        testfile = os.path.join(self.path, 'data','vol1_data','2009',
                                '01_Prelim','2009-01-10_115326','Vol1',
                                 'data','20090110_115326_AVAB_2A.V1A')
        v1 = Vol12Reader(testfile,headonly=False)

    def test_Vol2Reader(self):
        testfile = os.path.join(self.path, 'data', '19900210032700E_Vol2_o90400A1.V2A')
        v2 = Vol12Reader(testfile,headonly=False)
        self.assertEqual(len(v2.stream),9)
        self.assertEqual(round(abs(v2.stream[2].data).max(),2),0.76)
        self.assertEqual(round(abs(v2.stream[-3].data).max(),1),20.2)

    def test_Vol2ReaderHeadOnly(self):
        testfile = os.path.join(self.path, 'data', '19900210032700E_Vol2_o90400A1.V2A')
        v2 = Vol12Reader(testfile,headonly=True)
        self.assertEqual(v2.stream[0].stats.smdict.site,'400A')
        self.assertEqual(v2.stream[1].data.size,0)
        self.assertEqual(v2.stream[0].stats.smdict.compdir,90)

    def test_Vol2ReaderDummy(self):
        v = Vol12Reader(dummy=True)

def suite():
    return unittest.makeSuite(GNSSmTestCase, 'test')


if __name__ == '__main__': # pragma: no cover
    unittest.main(defaultTest='suite')
