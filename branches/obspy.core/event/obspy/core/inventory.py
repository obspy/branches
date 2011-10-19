# -*- coding: utf-8 -*-
"""
Module for handling ObsPy Inventory objects.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from obspy.core.util import AttribDict

from lxml import etree


class Inventory(object):
    """
    """
    def __init__(self, networks=None):
        """
        XXX: Missing stuff
        :type networks: list
        :param networks: List of :class:
        """
        self.networks = []
        if networks:
            self.networks.extend(networks)


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


def readStationXML(filename):
    """
    """
    doc = etree.parse(filename)
    from IPython.core.debugger import Tracer; Tracer()()
