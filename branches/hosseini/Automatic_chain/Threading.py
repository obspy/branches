#!/usr/bin/python

import threading
import time
from Main import *

exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        self.threadID = threadID
        self.name = name
        self.counter = counter
        threading.Thread.__init__(self)
    def run(self):
        print "Starting " + self.name
        Main()
        print "Exiting " + self.name


thread = myThread(1, 'Thread-1', 1)
thread2 = myThread(2, 'Thread-2', 2)

thread.start()
#thread2.start()
