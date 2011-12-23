# -*- coding: utf-8 -*-
"""
Module for handling ObsPy Catalog and Event objects.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from glob import glob, iglob, has_magic
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.util import NamedTemporaryFile, getExampleFile, uncompressFile
from obspy.core.util.attribdict import AttribDict
import os
import urllib2
try:
    # try using lxml as it is faster
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree


def readQuakeML(pathname_or_url=None):
    """
    Read QuakeML files into an ObsPy Catalog object.

    The :func:`~obspy.core.event.readQuakeML` function opens either one or
    multiple QuakeML formated event files given via file name or URL using the
    ``pathname_or_url`` attribute.

    :type pathname_or_url: string, optional
    :param pathname_or_url: String containing a file name or a URL. Wildcards
        are allowed for a file name. If this attribute is omitted, a Catalog
        object with an example data set will be created.
    :type format: string, optional
    :return: A ObsPy :class:`~obspy.core.event.Catalog` object.
    """
    # if no pathname or URL specified, make example stream
    if not pathname_or_url:
        return _createExampleCatalog()
    # if pathname starts with /path/to/ try to search in examples
    if isinstance(pathname_or_url, basestring) and \
       pathname_or_url.startswith('/path/to/'):
        try:
            pathname_or_url = getExampleFile(pathname_or_url[9:])
        except:
            # otherwise just try to read the given /path/to folder
            pass
    # create catalog
    cat = Catalog()
    if "://" in pathname_or_url:
        # extract extension if any
        suffix = os.path.basename(pathname_or_url).partition('.')[2] or '.tmp'
        # some URL
        fh = NamedTemporaryFile(suffix=suffix)
        fh.write(urllib2.urlopen(pathname_or_url).read())
        fh.close()
        cat.extend(_readQuakeML(fh.name).events)
        os.remove(fh.name)
    else:
        # file name
        pathname = pathname_or_url
        for file in iglob(pathname):
            cat.extend(_readQuakeML(file).events)
        if len(cat) == 0:
            # try to give more specific information why the stream is empty
            if has_magic(pathname) and not glob(pathname):
                raise Exception("No file matching file pattern: %s" % pathname)
            elif not has_magic(pathname) and not os.path.isfile(pathname):
                raise IOError(2, "No such file or directory", pathname)
    return cat


@uncompressFile
def _readQuakeML(filename):
    """
    Reads a single QuakeML file and returns a ObsPy Catalog object.
    """
    xml_doc = etree.parse(filename)
    catalog = Catalog()
    for event_xml in __xml2obj(xml_doc.getroot(), 'eventParameters/event'):
        # create new Event object
        event = Event()
        # preferred items
        preferred_origin = __xml2obj(event_xml, 'preferredOriginID', str)
        preferred_magnitude = __xml2obj(event_xml, 'preferredMagnitudeID', str)
        preferred_focal_mechanism = \
            __xml2obj(event_xml, 'preferredFocalMechanismID', str)
        # event type
        event.type = __xml2obj(event_xml, 'type', str)
        # creation info
        event.creation_info = AttribDict()
        event.creation_info.agency_uri = \
            __xml2obj(event_xml, 'creationInfo/agencyURI', str)
        event.creation_info.author_uri = \
            __xml2obj(event_xml, 'creationInfo/authorURI', str)
        event.creation_info.creation_time = \
            __xml2obj(event_xml, 'creationInfo/creationTime', UTCDateTime)
        event.creation_info.version = \
            __xml2obj(event_xml, 'creationInfo/version', str)
        # description
        event.description = AttribDict()
        event.description.type = __xml2obj(event_xml, 'description/type', str)
        event.description.text = __xml2obj(event_xml, 'description/text', str)
        # origins
        event.origins = []
        for origin_xml in __xml2obj(event_xml, 'origin'):
            origin = Origin()
            origin.public_id = origin_xml.get('publicID')
            origin.time = __xml2obj(origin_xml, 'time/value', UTCDateTime)
            origin.time_uncertainty = \
                __xml2obj(origin_xml, 'time/uncertainty', float)
            origin.latitude = __xml2obj(origin_xml, 'latitude/value', float)
            origin.latitude_uncertainty = \
                __xml2obj(origin_xml, 'latitude/uncertainty', float)
            origin.longitude = __xml2obj(origin_xml, 'longitude/value', float)
            origin.longitude_uncertainty = \
                __xml2obj(origin_xml, 'longitude/uncertainty', float)
            origin.depth = __xml2obj(origin_xml, 'depth/value', float)
            origin.depth_uncertainty = \
                __xml2obj(origin_xml, 'depth/uncertainty', float)
            origin.depth_type = __xml2obj(origin_xml, 'depthType', str)
            origin.method_id = __xml2obj(origin_xml, 'depthType', str)
            # quality
            origin.quality.used_station_count = \
                __xml2obj(origin_xml, 'quality/usedStationCount', int)
            origin.quality.standard_error = \
                __xml2obj(origin_xml, 'quality/standardError', float)
            origin.quality.azimuthal_gap = \
                __xml2obj(origin_xml, 'quality/azimuthalGap', float)
            origin.quality.maximum_distance = \
                __xml2obj(origin_xml, 'quality/maximumDistance', float)
            origin.quality.minimum_distance = \
                __xml2obj(origin_xml, 'quality/minimumDistance', float)
            origin.type = __xml2obj(origin_xml, 'type', str)
            origin.evaluation_mode = \
                __xml2obj(origin_xml, 'evaluationMode', str)
            origin.evaluation_status = \
                __xml2obj(origin_xml, 'evaluationStatus', str)
            origin.comment = __xml2obj(origin_xml, 'comment', str)
            # creationInfo
            origin.creation_info.agency_uri = \
                __xml2obj(origin_xml, 'creationInfo/agencyURI', str)
            origin.creation_info.author_uri = \
                __xml2obj(origin_xml, 'creationInfo/authorURI', str)
            # originUncertainty
            origin.origin_uncertainty.min_horizontal_uncertainty = \
                __xml2obj(origin_xml,
                          'originUncertainty/minHorizontalUncertainty', float)
            origin.origin_uncertainty.max_horizontal_uncertainty = \
                __xml2obj(origin_xml,
                          'originUncertainty/maxHorizontalUncertainty', float)
            origin.origin_uncertainty.azimuth_max_horizontal_uncertainty = \
                __xml2obj(origin_xml,
                          'originUncertainty/azimuthMaxHorizontalUncertainty',
                          float)
            # add preferred origin to front
            if origin.public_id == preferred_origin:
                event.origins.insert(0, origin)
            else:
                event.origins.append(origin)
        # magnitudes
        event.magnitudes = []
        for mag_xml in __xml2obj(event_xml, 'magnitude'):
            magnitude = Origin()
            magnitude.public_id = mag_xml.get('publicID')
            magnitude.magnitude = __xml2obj(mag_xml, 'mag/value', float)
            magnitude.magnitude_uncertainty = \
                __xml2obj(mag_xml, 'mag/uncertainty', float)
            magnitude.type = __xml2obj(mag_xml, 'type', str)
            magnitude.origin_id = __xml2obj(mag_xml, 'originID', str)
            magnitude.station_count = __xml2obj(mag_xml, 'stationCount', int)
            # creationInfo
            magnitude.creation_info.agency_uri = \
                __xml2obj(origin_xml, 'creationInfo/agencyURI', str)
            magnitude.creation_info.author_uri = \
                __xml2obj(origin_xml, 'creationInfo/authorURI', str)
            # add preferred magnitude to front
            if magnitude.public_id == preferred_magnitude:
                event.magnitudes.insert(0, magnitude)
            else:
                event.magnitudes.append(magnitude)
        # add current event to catalog
        catalog.append(event)
    return catalog


def writeQuakeML(catalog):
    """
    Writes a QuakeML file from given ObsPy Catalog or Event object.
    """
    raise NotImplementedError


def __xml2obj(xml_doc, xpath, convert_to=None,
              namespace='http://quakeml.org/xmlns/quakeml/1.0'):
    """
    """
    parts = xpath.split('/')
    ns = '/{%s}' % (namespace)
    xpath = (ns + ns.join(parts))[1:]
    if convert_to is None:
        return xml_doc.findall(xpath)
    text = xml_doc.findtext(xpath)
    # empty/not set datetimes should return None
    if convert_to == UTCDateTime and not text:
        return None
    # str(None) should be ''
    if convert_to == str and text is None:
        return ''
    # try to convert into requested type
    try:
        return convert_to(text)
    except:
        return None


def _createExampleCatalog():
    """
    Create an example catalog.
    """
    cat = Catalog()
    return cat


class Origin(AttribDict):
    """
    Contains a single earthquake origin.
    """
    public_id = None
    time = None
    latitude = None
    longitude = None
    quality = AttribDict()
    creation_info = AttribDict()
    origin_uncertainty = AttribDict()

    def __str__(self):
        return "%s (%.3f, %.3f)" % \
            (self.time, self.latitude, self.longitude)


class Magnitude(AttribDict):
    """
    Contains a single earthquake magnitude.
    """
    public_id = None
    magnitude = None
    creation_info = AttribDict()

    def __str__(self):
        return "%.3f" % self.magnitude


class Event(AttribDict):
    """
    Seismological event containing origins, picks, magnitudes, etc.
    """
    origins = []
    magnitudes = []
    amplitudes = []
    picks = []
    focal_mechanism = []
    station_magnitudes = []
    type = None

    def __str__(self):
        out = '%s (%.3f, %.3f)' % (self.preferred_origin.time,
                                   self.preferred_origin.latitude,
                                   self.preferred_origin.longitude)
        if self.preferred_magnitude:
            out += ' - %s %s' % (self.preferred_magnitude.magnitude,
                                 self.preferred_magnitude.type)
        if self.preferred_origin.evaluation_mode:
            out += ' - %s' % (self.preferred_origin.evaluation_mode)
        return out

    def getPreferredMagnitude(self):
        if self.magnitudes:
            return self.magnitudes[0]
        return None

    preferred_magnitude = property(getPreferredMagnitude)

    def getPreferredMagnitudeID(self):
        if self.magnitudes:
            return self.magnitudes[0].public_id
        return None

    preferred_magnitude_id = property(getPreferredMagnitudeID)

    def getPreferredOrigin(self):
        if self.origins:
            return self.origins[0]
        return None

    preferred_origin = property(getPreferredOrigin)

    def getPreferredOriginID(self):
        if self.origins:
            return self.origins[0].public_id
        return None

    preferred_origin_id = property(getPreferredOriginID)

    def getPreferredFocalMechanism(self):
        if self.focal_mechanism:
            return self.focal_mechanism[0]
        return None

    preferred_focal_mechanism = property(getPreferredFocalMechanism)

    def getPreferredFocalMechanismID(self):
        if self.focal_mechanism:
            return self.focal_mechanism[0].public_id
        return None

    preferred_focal_mechanism_id = property(getPreferredFocalMechanismID)


class Catalog(object):
    """
    Seismological event catalog containing a list of events.
    """
    def __init__(self, events=None):
        self.events = []
        if events:
            self.events.extend(events)

    def __add__(self, other):
        """
        Method to add two catalogs.
        """
        if isinstance(other, Event):
            other = Catalog([other])
        if not isinstance(other, Catalog):
            raise TypeError
        events = self.events + other.events
        return self.__class__(events=events)

    def __iadd__(self, other):
        """
        Method to add two catalog with self += other.

        It will extend the current Catalog object with the events of the given
        Catalog. Events will not be copied but references to the original
        events will be appended.

        :type other: :class:`~obspy.core.event.Catalog` or
            :class:`~obspy.core.event.Event`
        :param other: Catalog or Event object to add.
        """
        if isinstance(other, Event):
            other = Catalog([other])
        if not isinstance(other, Catalog):
            raise TypeError
        self.extend(other.events)
        return self

    def __iter__(self):
        """
        Return a robust iterator for Events of current Catalog.

        Doing this it is safe to remove events from catalogs inside of
        for-loops using catalog's :meth:`~obspy.core.event.Catalog.remove`
        method. Actually this creates a new iterator every time a event is
        removed inside the for-loop.
        """
        return list(self.events).__iter__()

    def __len__(self):
        """
        Returns the number of Events in the Catalog object.
        """
        return len(self.events)

    count = __len__

    def __str__(self):
        """
        Returns short summary string of the current catalog.

        It will contain the number of Events in the Catalog and the return
        value of each Event's :meth:`~obspy.core.event.Event.__str__` method.
        """
        out = str(len(self.events)) + ' Event(s) in Catalog:\n'
        out = out + "\n".join([ev.__str__() for ev in self])
        return out

    def __getitem__(self, index):
        """
        __getitem__ method of obspy.core.Catalog objects.

        :return: Event objects
        """
        if isinstance(index, slice):
            return self.__class__(events=self.events.__getitem__(index))
        else:
            return self.events.__getitem__(index)

    def append(self, event):
        """
        Appends a single Event object to the current Catalog object.
        """
        if isinstance(event, Event):
            self.events.append(event)
        else:
            msg = 'Append only supports a single Event object as an argument.'
            raise TypeError(msg)

    def extend(self, event_list):
        """
        Extends the current Catalog object with a list of Event objects.
        """
        if isinstance(event_list, list):
            for _i in event_list:
                # Make sure each item in the list is a event.
                if not isinstance(_i, Event):
                    msg = 'Extend only accepts a list of Event objects.'
                    raise TypeError(msg)
            self.events.extend(event_list)
        elif isinstance(event_list, Catalog):
            self.extend(event_list.traces)
        else:
            msg = 'Extend only supports a list of Event objects as argument.'
            raise TypeError(msg)

    def write(self, filename, format):
        """
        Exports catalog to file system using given format.
        """
        raise NotImplementedError

    def plot(self, *args, **kwargs):
        """
        Creates preview map of all events in current Catalog object.
        """
        from mpl_toolkits.basemap import Basemap
        import matplotlib.pyplot as plt
        map = Basemap(resolution='l')
        # draw coastlines, country boundaries, fill continents.
        map.drawcoastlines()
        map.drawcountries()
        map.fillcontinents(color = '#EEEEEE')
        # draw the edge of the map projection region (the projection limb)
        map.drawmapboundary()
        # lat/lon coordinates
        lats = []
        lons = []
        labels = []
        for event in self.events:
            lats.append(event.preferred_origin.latitude)
            lons.append(event.preferred_origin.longitude)
            labels.append(event.preferred_origin.time)
        # compute the native map projection coordinates for events.
        x, y = map(lons, lats)
        # plot filled circles at the locations of the events.
        map.plot(x, y, 'ro')
        # plot labels
        for name, xpt, ypt in zip(labels, x, y):
            plt.text(xpt, ypt, name, size='small')
        plt.show()


if __name__ == '__main__':
    import StringIO
    from obspy.neries import Client
    data = Client(user='test@obspy.org').getLatestEvents(20)
    cat = _readQuakeML(StringIO.StringIO(data))
    #cat = readQuakeML('quakeml.xml')
    print cat
    cat.plot()
