# -*- coding: utf-8 -*-
"""
Module for handling ObsPy Inventory objects.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from obspy.core import UTCDateTime
from obspy.core.util import AttribDict

from lxml import etree


class Inventory(object):
    """
    """
    def __init__(self, networks=[]):
        """
        XXX: Missing stuff
        :type networks: list
        :param networks: List of :class:
        """
        self.networks = []
        if networks:
            self.networks.extend(networks)
        # Set a stats attribute for format specific informations.
        self.stats = AttribDict()

    def __len__(self):
        """
        Returns the available number of stations in the inventory file.
        """
        return len(self.networks)

    def __str__(self):
        networks = []
        for net in self.networks:
            networks.extend(net.__str__().split('\n'))
        return ('%i networks in the inventory:\n\t' % len(self)) + \
                '\n\t'.join(networks)


class Network(object):
    """
    """
    def __init__(self, network_code, stations=None, **kwargs):
        """
        Possible keyword arguments
        --------------------------
        :param description:
        :param starttime:
        :param endtime:
        :type total_number_of_stations: integer
        :param total_number_of_stations: The total number of stations contained
            in this network, including inactive or terminated stations.
        """
        self.network_code = network_code
        self.stations = []
        if stations:
            self.stations.extend(stations)
        self.description = kwargs.get('description', None)
        self.starttime = kwargs.get('starttime', None)
        self.endtime = kwargs.get('endtime', None)

    def __len__(self):
        return len(self.stations)

    def __str__(self):
        ret = 'Network %s, %s - %s' % (self.network_code,
                                       self.starttime.strftime('%Y-%m-%d'),
                                    self.endtime.strftime('%Y-%m-%d'))
        if not hasattr(self, 'total_number_of_stations'):
            ret += '\n\t%i stations in network' % len(self)
        else:
            ret += '\n\t%i stations in network (%i actually in object)' % \
                (self.total_number_of_stations, len(self))
        if self.description:
            ret += '\n\tDescription: %s' % self.description
        return ret


class Station(object):
    """
    """
    def __init__(self, station_code, channels=[], **kwargs):
        """
        """
        self.station_code = station_code
        self.channels = []
        if channels:
            self.channels.extend(channels)

        self.starttime = kwargs.get('starttime', None)
        self.endtime = kwargs.get('endtime', None)

        self.latitude = kwargs.get('latitude', None)
        self.longitude = kwargs.get('longitude', None)
        self.elevation = kwargs.get('elevation', None)

        self.site = AttribDict()
        self.site.town = kwargs.get('site_town', None)
        self.site.county = kwargs.get('site_county', None)
        self.site.state = kwargs.get('site_state', None)
        self.site.country = kwargs.get('site_country', None)

        self.common_name = kwargs.get('common_name', None)
        self.description = kwargs.get('description', None)

        self.creation_date = kwargs.get('creation_date', None)


class Channel(object):
    """
    """
    def __init__(self, channel_code, location_code, responses=[], **kwargs):
        """
        """
        self.channel_code = channel_code
        self.location_code = location_code

        self.starttime = kwargs.get('starttime', None)
        self.endtime = kwargs.get('endtime', None)

        self.creation_date = kwargs.get('creation_date', None)

        self.latitude = kwargs.get('latitude', None)
        self.longitude = kwargs.get('longitude', None)
        self.elevation = kwargs.get('elevation', None)
        self.depth = kwargs.get('depth', None)
        self.azimuth = kwargs.get('azimuth', None)
        self.dip = kwargs.get('dip', None)
        self.sampling_rate = kwargs.get('sampling_rate', None)
        self.clock_drift = kwargs.get('clock_drift', None)

        self.sensor = AttribDict()
        self.sensor.equip_type = kwargs.get('equip_type', None)

        self.instrument_sensitivity = AttribDict()
        self.instrument_sensitivity.value = kwargs.get('sensitivity_value',
                                                       None)
        self.instrument_sensitivity.frequency = \
            kwargs.get('sensitivity_frequency', None)
        self.instrument_sensitivity.units = \
            kwargs.get('sensitivity_units', None)

        self.responses = []
        if responses:
            self.responses.extend(responses)


class Response(object):
    def __init__(self, stage, **kwargs):
        self.stage = stage

        self.stage_sensitivity = AttribDict()
        self.stage_sensitivity.value = kwargs.get('sensitivity_value', None)
        self.stage_sensitivity.gain_units = \
            kwargs.get('sensitivity_gain_units', None)
        self.stage_sensitivity.frequency = \
            kwargs.get('sensitivity_frequency', None)

        self.decimation = AttribDict()
        self.decimation.input_sample_rate = \
            kwargs.get('decimation_input_sample_rate', None)
        self.decimation.factor = kwargs.get('decimation_factor', None)
        self.decimation.offset = kwargs.get('decimation_offset', None)
        self.decimation.delay = kwargs.get('decimation_delay', None)
        self.decimation.correction = kwargs.get('decimation_correction', None)


class PoleZeroResponse(Response):
    def __init__(self, poles=[], zeros=[], **kwargs):
        Response.__init__(self, **kwargs)

        self.poles = poles
        self.zeros = zeros

        self.comment = kwargs('comment', None)
        self.input_units = kwargs('input_units', None)
        self.output_units = kwargs('output_units', 'COUNTS')
        self.normalization_factor = kwargs('normalization_factor', 1.0)
        self.normalization_frequency = kwargs('normalization_frequency', None)


class CoefficientResponse(Response):
    def __init__(self, input_units, output_units, **kwargs):
        Response.__init__(self, **kwargs)
        self.input_units = input_units
        self.output_units = output_units
        self.numerator = kwargs.get('numerator', [])
        self.denominator = kwargs.get('denominator', [])


def __addFormatSpecificData(doc, nsmap, stats_object, xml_node,
                            conversion=None):
    """
    Adds the text of and xml_node in doc with the ns namespace in nsmap to
    stats_object as attribute stats_name.

    :param conversion: Function/Constructor that will take the xml text as
        input and return an object that will be attached to stats_object.
    """
    item = doc.findall('ns:%s' % xml_node, namespaces=nsmap)
    if len(item) == 1:
        if conversion is None:
            setattr(stats_object, xml_node, item[0].text)
        else:
            setattr(stats_object, xml_node, conversion(item[0].text))


def readStationXML(filename):
    """
    """
    inventory = Inventory()

    doc = etree.parse(filename)
    # Get the default namespace.
    root = doc.getroot()
    nsmap = root.nsmap
    nsmap['ns'] = nsmap[None]

    # Read some format specific data.
    inventory.stats.station_xml = AttribDict()
    s_xml_stats = inventory.stats.station_xml
    __addFormatSpecificData(doc, nsmap, s_xml_stats, 'Source')
    __addFormatSpecificData(doc, nsmap, s_xml_stats, 'Sender')
    __addFormatSpecificData(doc, nsmap, s_xml_stats, 'Module')
    __addFormatSpecificData(doc, nsmap, s_xml_stats, 'ModuleURI')
    __addFormatSpecificData(doc, nsmap, s_xml_stats, 'SentDate',
                            conversion=UTCDateTime)

    networks = doc.findall('ns:Network', namespaces=nsmap)
    for network in networks:
        n_obj = Network(network_code=network.get('net_code', ''))
        try:
            n_obj.starttime = UTCDateTime(network.find('ns:StartDate',
                                                       namespaces=nsmap).text)
        except AttributeError:
            pass
        try:
            n_obj.endtime = UTCDateTime(network.find('ns:EndDate',
                                                       namespaces=nsmap).text)
        except AttributeError:
            pass
        try:
            n_obj.description = network.find('ns:Description',
                                             namespaces=nsmap).text
        except AttributeError:
            pass
        try:
            n_obj.total_number_of_stations = \
                int(network.find('ns:TotalNumberStations',
                                 namespaces=nsmap).text)
        except AttributeError:
            pass
        inventory.networks.append(n_obj)
    return inventory


def __convertUTCDateTimeToStationXMLString(dt):
    """
    Converts a UTCDateTime to a string in the StationXML representation.
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def __addSubelement(root, element_name, stats):
    if not hasattr(stats, element_name):
        return
    element = etree.SubElement(root, element_name)
    text = getattr(stats, element_name)
    if isinstance(text, UTCDateTime):
        text = __convertUTCDateTimeToStationXMLString(text)
    element.text = text


def __addNetworkToElement(doc, network):
    net = etree.SubElement(doc, 'Network')
    net.set('net_code', network.network_code)
    sub = etree.SubElement(net, 'StartDate')
    sub.text = __convertUTCDateTimeToStationXMLString(network.starttime)
    sub = etree.SubElement(net, 'EndDate')
    sub.text = __convertUTCDateTimeToStationXMLString(network.endtime)
    if hasattr(network, 'description'):
        sub = etree.SubElement(net, 'Description')
        sub.text = network.description
    if hasattr(network, 'total_number_of_stations'):
        sub = etree.SubElement(net, 'TotalNumberStations')
        sub.text = str(network.total_number_of_stations)


def writeStationXML(inventory, file_object):
    """
    Writes the data in inventory as StationXML to file_object.
    """
    # Define namespace.
    nsmap = {None: 'http://www.data.scec.org/xml/station/',
             'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    # Create the root element with namespaces and other things.
    doc = etree.Element('StaMessage', nsmap=nsmap)
    doc.set('{%s}schemaLocation' % nsmap['xsi'],
            'http://www.data.scec.org/xml/station/ ' +\
            'http://www.data.scec.org/xml/station/station.xsd')
    # Add the station xml specific subelements.
    __addSubelement(doc, 'Source', inventory.stats.station_xml)
    __addSubelement(doc, 'Sender', inventory.stats.station_xml)
    __addSubelement(doc, 'Module', inventory.stats.station_xml)
    __addSubelement(doc, 'ModuleURI', inventory.stats.station_xml)
    __addSubelement(doc, 'SentDate', inventory.stats.station_xml)

    for network in inventory.networks:
        __addNetworkToElement(doc, network)

    file_object.write(etree.tostring(doc, pretty_print=True))
