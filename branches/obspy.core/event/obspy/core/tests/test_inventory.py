# -*- coding: utf-8 -*-

from obspy.core.inventory import readStationXML

import os
import unittest


class InventoryTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        # Directory where the test files are located
        self.path = os.path.join(os.path.dirname(__file__), 'data')

    def test_readStationXMLNetwork(self):
        filename = os.path.join(self.path, 'iris_net.xml')
        inventory = readStationXML(filename)



def suite():
    return unittest.makeSuite(InventoryTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
