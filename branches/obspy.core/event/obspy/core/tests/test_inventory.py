# -*- coding: utf-8 -*-

from obspy.core.inventory import readStationXML, writeStationXML

from itertools import izip
import os
from StringIO import StringIO
import unittest


class InventoryTestCase(unittest.TestCase):
    """
    """
    def setUp(self):
        # Directory where the test files are located
        self.path = os.path.join(os.path.dirname(__file__), 'data')

    def test_readAndWriteStationXMLNetwork(self):
        """
        Reading and writing a file should not change it.
        """
        filename = os.path.join(self.path, 'iris_net.xml')
        # Read to inventory object.
        inventory = readStationXML(filename)
        # Write to empty StringIO.
        new_xml = StringIO()
        writeStationXML(inventory, new_xml)
        new_xml.seek(0,0)

        # Test line by line for easier debugging and not having to worry about
        # formatting issues.
        with open(filename, 'r') as f:
            old_xml = StringIO(f.read())
        self.assertEqual(old_xml.tell(), new_xml.tell())
        for old_line, new_line in izip(old_xml, new_xml):
            self.assertEqual(old_line.strip(), new_line.strip())
        # Sanity check to ensure everything has been read.
        self.assertEqual(new_xml.tell(), new_xml.len)
        self.assertEqual(old_xml.tell(), old_xml.len)





def suite():
    return unittest.makeSuite(InventoryTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
