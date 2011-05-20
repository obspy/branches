#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A program that installs, un-installs or updates an ObsPy environment.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

import sys
import os
import urllib


DEFAULT_MODULES = ['core', 'gse2', 'mseed', 'sac', 'wav', 'signal', 'imaging',
                   'xseed', 'seisan', 'sh', 'segy']
ALL_MODULES = DEFAULT_MODULES + ['arclink', 'seishub', 'iris', 'neries', 'db']
DEPENDENCIES = ['numpy', 'scipy', 'matplotlib', 'lxml']


def isVirtualEnv():
    """
    Check if we have been called within a virtual environment.
    http://stackoverflow.com/questions/1871549/python-determine-if-running-inside-virtualenv
    """
    return hasattr(sys, 'real_prefix')


def hasVirtualEnv():
    """
    Check if module virtualenv has been installed.
    """
    if sys.hexversion < 0x03000000:
        # Python 2
        try:
            import virtualenv
        except:
            return False
    else:
        # Python 3
        try:
            import virtualenv3
        except:
            return False
    return True


def hasSetupTools():
    """
    Check if module distribute has been installed.
    """
    try:
        import setuptools
    except:
        return False
    return True


def getInstalledObsPyModules():
    for module in sorted(ALL_MODULES):
        try:
            mod = __import__('obspy.' + module, fromlist='obspy')
            print module, mod.__version__
        except:
            pass


def getCurrentObsPyRevision():
    data = urllib.urlopen("https://svn.obspy.org").read()
    return int(data.partition('Revision')[2].partition(':')[0])


def getCurrentObsPyModuleVersions():
    out = []
    for module in sorted(ALL_MODULES):
        url = "http://pypi.python.org/pypi?:action=doap&name=obspy.%s"
        data = urllib.urlopen(url % (module)).read()
        version = data.partition('<revision>')[2].partition('</revision>')[0]
        help = data.partition('<shortdesc>')[2].partition('</shortdesc>')[0]
        out.append((module, version, help))
    return out


def main():
    print("ObsPy setup script")
    print("\nChecking environment ...")
    print("  * has setuptools: %s" % hasSetupTools())
    print("  * has virtualenv: %s" % hasVirtualEnv())
    print("  * is virtualenv: %s" % isVirtualEnv())
    print("\nFetching available modules")
    print("  * current developer revision: %s" % getCurrentObsPyRevision())
    print("  * available modules on PyPI:")
    for module, version, _ in getCurrentObsPyModuleVersions():
        print("    * obspy.%s, %s" % (module, version))
    print("installed modules: %s" % getInstalledObsPyModules())


if __name__ == "__main__":
    main()
