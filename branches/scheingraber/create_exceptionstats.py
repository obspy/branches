#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to create statistics from one or more exceptions.txt files.
Run inside a directory of a finished project to obtain statistics.
"""

from operator import itemgetter
from lxml import etree
import pickle

# INPUT
# list of filenames
exfiles = ["exceptions.txt"]
# minimum amount of distinct channels in network to be included in table
min_channels = 10
# max number of best and worst networks to be listed in exceptions table
max_networks = 5

########################################################################


def main():
    # dictionary to hold statistics
    exdict = {'ArcLink' : {}, 'IRIS' : {}}

    # open files and read into string
    for exfile in exfiles:
        exceptionsfin = open(exfile, 'rt')
        exceptions = exceptionsfin.readlines()
        exceptionsfin.close()
        for exception in exceptions[3:]:
            # dealing with some (few) messed up exception strings
            try:
                (event, provider, identifier, s, e, msg) = exception.split(';')
            except:
                continue
            # create dict for this event if not existing yet
            exdict[provider].setdefault(event, {})
            # get network
            network = identifier.split('.')[0]
            # create dict for this network if not existing yet
            exdict[provider][event].setdefault(network, {})
            # set dict to msg:
            # This way, if the files contain duplicate
            # exceptions for the same event+identifier, we just count it once
            exdict[provider][event][network][identifier] = msg

    # prepare inner stats dict for arclink
    arcstats = {'total' : 0, 'no data' : 0, 'timeout' : 0, 'no content' : 0,
                'unset' : 0, 'refused' : 0, 'no route' : 0, 'other' : 0,
                'nwstats' : {}}
    # for iris, there are these exceptions, always saying no data
    # 404 not found
    # 403 forbidden
    # 500 internal server error
    # 503 service unavailable

    # and these urlopen errors:
    # Connection refused
    # urlopen error timed out
    irisstats = {'403' : 0, '404' : 0, '500' : 0,'503' : 0, 'total' : 0,
                 'other' : 0, 'timeout' : 0, 'refused' : 0, 'nwstats' : {}}

    stats = {'ArcLink' : arcstats, 'IRIS' : irisstats}

    # obtain statistics, this was not done above to be able to deal with multiple
    # files at once and to add more detailed statistics in future if necessary
    for (provider, events) in exdict.items():
        for (event, networks) in events.items():
            for (network, identifier) in networks.items():
                for (identifier, exception) in identifier.items():
                    # increment total
                    stats[provider]['total'] += 1
                    # set default exceptions to 0 for this key if it doesn't exist
                    stats[provider]['nwstats'].setdefault(network, 0)
                    # now increment the network exception count
                    stats[provider]['nwstats'][network] += 1
                    # these are same for both providers
                    if 'refused' in exception:
                        stats[provider]['refused'] += 1
                    elif 'timed out' in exception or 'Timeout' in exception:
                        stats[provider]['timeout'] += 1
                    elif 'refused' in exception:
                        stats[provider]['refused'] += 1
                    # some exceptions just for arclink
                    elif provider == 'ArcLink':
                        # check which exception
                        if 'data available' in exception:
                            stats[provider]['no data'] += 1
                        elif 'UNSET' in exception:
                            stats[provider]['unset'] += 1
                        elif 'No content' in exception:
                            stats[provider]['no content'] += 1
                        elif 'route' in exception:
                            stats[provider]['no route'] += 1
                        else:
                            stats[provider]['other'] += 1
                    # since IRIS always says "no data", we do some distinctions
                    else:  # IRIS
                        if 'Error 403' in exception:
                            stats[provider]['403'] += 1
                        elif 'Error 404' in exception:
                            stats[provider]['404'] += 1
                        elif 'Error 500' in exception:
                            stats[provider]['500'] += 1
                        elif 'Error 503' in exception:
                            stats[provider]['503'] += 1
                        else:
                            stats[provider]['other'] += 1

    # print statistics to screen
    for provider, stats2 in stats.items():
        print "\n\n"
        print "-" * 22
        print provider,
        print "exceptions"
        print "-" * 22
        print "type\t\tamount"
        print "-" * 22
        for key, val in stats2.items():
            if type(val) == int:
                if 'content' in key or 'route' in key:
                    print "%s\t%i" % (key, val)
                else:
                    print "%s\t\t%i" % (key, val)
    # obtain total number of stations attempted to download from each network
    iris_channels = get_iris_channels()
    arclink_channels = get_arclink_channels()
    # obtain number of events
    no_of_events = get_no_events()
    # create provider channel dict
    channels = {'ArcLink' : arclink_channels, 'IRIS' : iris_channels}
    for provider, stats2 in stats.items():
        # per network
        # create list to sort into by % values later.
        # Format, sorted by percent_exceptions:
        # [(percent_exceptions, network, no_of_channels, no_of_except),
        #   ..., (...)]
        exceptionstable = []
        total_nof_channels = 0
        for network, no_of_exceptions in stats2['nwstats'].items():
            # number of channels in network
            try:
                no_of_channels = channels[provider][network]
            except:
                # not same networks for both providers
                continue
            exceptionstable.append(
                        (no_of_exceptions*100.0/(no_of_channels*no_of_events),
                        network, no_of_channels, no_of_exceptions))
            total_nof_channels += no_of_channels
        # calculate total percentage of exceptions for data providers
        prc_total = stats[provider]['total'] * 100.0 \
                                          / (total_nof_channels * no_of_events)
        # print table
        print "\n\n"
        print "-" * 60
        print provider,
        print "networks with at least %i requested channels:" % min_channels
        print "-" * 60
        print "Network\t\t%successful\t#requests\t#exceptions"
        print "-" * 60
        exceptionstable.sort()
        printed = 0
        for perc, net, no_cha, no_exc in exceptionstable:
            if no_cha > min_channels and printed < max_networks:
                print "%s\t\t%.2f\t\t%i\t\t%i" % (net, 100-perc,
                                          no_cha*no_of_events, no_exc)
                printed += 1
        printed = 0
        print "...\t\t" * 4
        exceptionstable.sort(reverse=True)
        worst_str = ""
        for perc, net, no_cha, no_exc in exceptionstable:
            if no_cha > min_channels and printed < max_networks:
                worst_str = "%s\t\t%.2f\t\t%i\t\t%i\n" % (net, 100-perc,
                            no_cha*no_of_events, no_exc) + worst_str
                printed += 1
        print worst_str,
        print "-" * 60
        print "TOTAL\t\t%.2f\t\t%i\t\t%i" % (100-prc_total,
                                             total_nof_channels * no_of_events,
                                             stats[provider]['total'])
        print "-" * 60


def get_iris_channels():
    """
    Reads IRIS availability pickle dump file from project directory to obtain
    the total number of channels that were attempted to download.
    Returns dictionary of networks with the respective amount of channels.
    """
    try:
        # load availability file
        availfp = 'availability.pickle'
        fh = open(availfp, 'rb')
        avail_list = pickle.load(fh)
        fh.close()
    except:
        return []
    # create stats dict to return later
    stats = {}
    #for old projects / pickle dump files
    #for (net, sta, cha, loc, lat, lon) in avail_list:
    for (net, sta, cha, loc, lat, lon, elevation) in avail_list:
        # just increment this networks' channel count by 1
        stats.setdefault(net, 0)
        stats[net] += 1
    return stats


def get_arclink_channels():
    """
    Reads ArcLink inventory pickle dump file from project directory to obtain
    the total number of channels that were attempted to download.
    Returns dictionary of networks with the respective amount of channels.
    """
    inventoryfp = 'inventory.pickle'
    try:
        fh = open(inventoryfp, 'rb')
        stations = pickle.load(fh)
        fh.close()
    except:
        return []
    # create stats dict to return later
    stats = {}
    for station in stations:
        station = station[0]
        net, sta, loc, cha = station.split('.')
        # just increment this networks' channel count by 1
        stats.setdefault(net, 0)
        stats[net] += 1
    return stats


def get_no_events():
    """
    Returns the number of events obtained from the events.pickle file.
    """
    eventfp = 'events.pickle'
    fh = open(eventfp, 'rb')
    events = pickle.load(fh)
    fh.close()
    return len(events)



if __name__ == "__main__":
    main()
