from StringIO import StringIO
from datetime import datetime
from lxml import etree, objectify
import os
import pytz
import re
import sys


class ObjectifiedDateTime(objectify.ObjectifiedDataElement):
    @property
    def pyval(self):
        result = re.match('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.?(\d{1,6})?Z?', str(self)).groups()
        if result[6]:
            values = map(int, result)
        else:
            values = map(int, result[:6])

        values.append(pytz.timezone("UTC"))

        return datetime(*values)

    @staticmethod
    def check(string):
        if not re.match("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.?\d{0,6}Z?", string):
            raise ValueError

xml_datetime_type = objectify.PyType('dateTime', ObjectifiedDateTime.check, ObjectifiedDateTime)
xml_datetime_type.xmlSchemaTypes = ('dateTime',)
xml_datetime_type.register()


class QMLParser(object):
    def __init__(self):
        # Patch XSD provided by QuakeML website to fit our needs
        xsd_path = os.path.join(os.path.dirname(__file__), 'QuakeML-BED-1.2.xsd')
        xsd_root = etree.parse(xsd_path).getroot()
        self.xsd_root = self.__patch_xsd(xsd_root)

        xsd_stringio =  StringIO(etree.tostring(self.xsd_root))
        self.parser = objectify.makeparser(schema=etree.XMLSchema(file=xsd_stringio))


    def __apply_attributes(self, obj):
        for attrname, value in obj.attrib.items():
            if attrname in ('channelCode', 'networkCode', 'publicID', 'stationCode'):
                setattr(obj, attrname, str(value))

        for obj in obj.__dict__.values():
            if isinstance(obj, objectify.ObjectifiedElement):
                map(self.__apply_attributes, obj)


    def __patch_xsd(self, root):
        del(root.attrib['targetNamespace'])


        # Remove any references to "bed" in "base" and "type" attributes
        #
        # attr.attrname not available with lxml 2.2
        # Can't use this code :
        # for attr in root.xpath('//@type | //@base'):
        #     if attr.startswith('bed:'):
        #         parent.attrib[attr.attrname] = attr[4:]
        for elem in root.xpath('//*[@type] | //*[@base]'):
            for attrname, attrvalue in elem.items():
                if attrvalue.startswith('bed:'):
                    elem.attrib[attrname] = attrvalue[4:]

        # Replace the first expected element (EventParameters) by Event element
        xsd_first_element = root.xpath("//*[@name='eventParameters']")[0]
        xsd_first_element.attrib['name'] = 'event'
        xsd_first_element.attrib['type'] = 'Event'

        # Remove publicID from Arrival
        arrival = root.xpath("//*[@name='Arrival']")[0]
        arrival_publicid = arrival.xpath(".//*[@name='publicID']")[0]
        arrival.remove(arrival_publicid)

        # Remove ResourceReference from WaveformstreamID
        waveformstreamid = root.xpath("//*[@name='WaveformStreamID']")[0]
        for elem in waveformstreamid.xpath(".//*[@name]"):
            waveformstreamid.append(elem)

        simplecontent = waveformstreamid.xpath("./*")[0]
        waveformstreamid.remove(simplecontent)

        # Remove any references to Namespaces in root element
        patched_root = etree.Element(root.tag, root.attrib)
        map(patched_root.append, root.getchildren())

        return patched_root


    def events(self, filename):
        for xml_event, elem in etree.iterparse(filename, tag='event'):
            xml_stringio = StringIO(etree.tostring(elem))
            elem.clear()

            obj = objectify.parse(xml_stringio, self.parser).getroot()
            self.__apply_attributes(obj)
            yield obj
