#! /usr/bin/env python

from lightqml import QMLParser
import sys

if __name__ == '__main__':
    qmlparser = QMLParser()
    for filename in sys.argv[1:]:
        for event in qmlparser.events(filename):
            print event.publicID
