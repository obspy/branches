#! /usr/bin/env python

from lxml import etree
import sys

if __name__ == '__main__':
    sys.stdout.write('<?xml version="1.0" encoding="utf-8"?>\n')
    sys.stdout.write('<quakeml xmlns:qml="http://quakeml.org/xmlns/quakeml/1.2rc3">\n')
    sys.stdout.write('<eventParameters publicID="smi:local/EventParameters/2010-12-07 15:58:58.269578">\n')

    for filename in sys.argv[1:]:
        for event, elem in etree.iterparse(filename, tag='event'):
            cleaned_elem = etree.Element(elem.tag, elem.attrib)
            map(cleaned_elem.append, elem.getchildren())

            print etree.tostring(cleaned_elem, pretty_print=True)

    sys.stdout.write('</eventParameters>\n')
    sys.stdout.write('</quakeml>\n')
