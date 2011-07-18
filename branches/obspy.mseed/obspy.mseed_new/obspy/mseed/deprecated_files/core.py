# -*- coding: utf-8 -*-
"""
MSEED bindings to ObsPy core module.

Deprecated. obspy.mseed.mseed will replace it.
"""

from obspy.mseed import mseed


def isMSEED(filename):
    """
    Deprecated. Will be passed to obspy.mseed.mseed.isMSEED.
    """
    return mseed.isMSEED(filename)


def readMSEED(filename, headonly=False, starttime=None, endtime=None,
              readMSInfo=True, reclen=-1, quality=False, **kwargs):
    """
    Reads a given Mini-SEED file and returns an Stream object.

    This function should NOT be called directly, it registers via the
    ObsPy :func:`~obspy.core.stream.read` function, call this instead.

    Parameters
    ----------
    filename : string
        Mini-SEED file to be read.
    headonly : bool, optional
        If set to True, read only the head. This is most useful for
        scanning available data in huge (temporary) data sets.
    starttime : :class:`~obspy.core.utcdatetime.UTCDateTime`, optional
        Specify the starttime to read. The remaining records are not
        extracted. Providing a starttime usually results into faster reading.
    endtime : :class:`~obspy.core.utcdatetime.UTCDateTime`, optional
        See description of starttime.
    readMSInfo : bool, optional
        If True the byteorder, record length and the encoding of the file will
        be read and stored in the Stream object. Only the very first record of
        the file will be read and all following records are assumed to be the
        same. Defaults to True.
    reclen : int, optional
        Record length in bytes of Mini-SEED file to read. This option might
        be usefull if blockette 10 is missing and thus read cannot
        determine the reclen automatically.
    quality : bool, optional
        Determines whether quality information is being read or not. Has a big
        impact on performance so only use when necessary (takes ~ 700 %
        longer). Two attributes will be written to each Trace's stats.mseed
        object: data_quality_flags_count counts the bits in field 14 of the
        fixed header for each Mini-SEED record. timing_quality is a
        `numpy.array` which contains all timing qualities found in Blockette
        1001 in the order of appearance. If no Blockette 1001 is found it will
        be an empty array.

    Example
    -------
    >>> from obspy.core import read # doctest: +SKIP
    >>> st = read("test.mseed") # doctest: +SKIP
    """
    __libmseed__ = LibMSEED()
    # Read fileformat information if necessary.
    if readMSInfo:
        info = __libmseed__.getFileformatInformation(filename)
        # Better readability.
        if 'reclen' in info:
            info['record_length'] = info['reclen']
            del info['reclen']
        if 'encoding' in info:
            info['encoding'] = ENCODINGS[info['encoding']][0]
        if 'byteorder' in info:
            if info['byteorder'] == 1:
                info['byteorder'] = '>'
            else:
                info['byteorder'] = '<'
    # read MiniSEED file
    if headonly:
        trace_list = __libmseed__.readMSHeader(filename, reclen=reclen)
    else:
        if platform.system() == "Windows" or quality:
            # 4x slower on Mac
            trace_list = __libmseed__.readMSTracesViaRecords(filename,
                         starttime=starttime, endtime=endtime, reclen=reclen,
                         quality=quality)
        else:
            # problem on windows with big files (>=20 MB)
            trace_list = __libmseed__.readMSTraces(filename, reclen,
                starttime=starttime, endtime=endtime)
    # Create a list containing all the traces.
    traces = []
    # Loop over all traces found in the file.
    for _i in trace_list:
        # Convert header to be compatible with obspy.core.
        old_header = _i[0]
        header = {}
        # Create a dictionary to specify how to convert keys.
        convert_dict = {'station': 'station', 'sampling_rate': 'samprate',
                        'npts': 'numsamples', 'network': 'network',
                        'location': 'location', 'channel': 'channel',
                        'starttime': 'starttime', 'endtime': 'endtime'}
        # Convert header.
        for _j, _k in convert_dict.iteritems():
            header[_j] = old_header[_k]
        # Dataquality is Mini-SEED only and thus has an extra Stats attribute.
        header['mseed'] = {}
        header['mseed']['dataquality'] = old_header['dataquality']
        # Convert times to obspy.UTCDateTime objects.
        header['starttime'] = \
            __libmseed__._convertMSTimeToDatetime(header['starttime'])
        header['endtime'] = \
            __libmseed__._convertMSTimeToDatetime(header['endtime'])
        # Append quality informations if necessary.
        if quality:
                header['mseed']['timing_quality'] = \
                np.array(old_header['timing_quality'])
                header['mseed']['data_quality_flags_count'] = \
                                      old_header['data_quality_flags']
        # Append information if necessary.
        if readMSInfo:
            for key, value in info.iteritems():
                header['mseed'][key] = value
        # Append traces.
        if headonly:
            header['npts'] = int((header['endtime'] - header['starttime']) *
                                   header['sampling_rate'] + 1 + 0.5)
            traces.append(Trace(header=header))
        else:
            traces.append(Trace(header=header, data=_i[1]))
    return Stream(traces=traces)


def writeMSEED(stream, filename, encoding=None, **kwargs):
    """
    Deprecated. All arguments will be passed to obspy.mseed.mseed.writeMSEED.
    """
    mseed.writeMSEED(stream, filename, encoding=encoding, **kwargs)
