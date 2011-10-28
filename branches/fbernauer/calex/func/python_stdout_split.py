#! /usr/bin/env python

import sys

class SplitWriter():
    """ 
    Implements a write method that writes a given message on all children
    """
    def __init__(self, filehandle):
        """ 
        Remember provided objects as children.
        """
        self.file = filehandle
        self.stdout = sys.stdout

    def write(self, msg):
        """ 
        Sends msg to all childrens write method.
        """
        self.stdout.write(msg)
        self.file.write(msg)


f = open("blibla", "wt")
sys.stdout = SplitWriter(f)



print "huhu"
print "haha"



f.close()
