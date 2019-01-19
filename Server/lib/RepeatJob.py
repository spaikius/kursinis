# -*- coding: utf-8 -*-

import threading 
import time

class RepeatJob(object):
    """Repeats function call"""
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval # time interval in sec
        self.function = function # Function for callback
        self.args = args # Callback functions parameters
        self.kwargs = kwargs #Callback functions parameters
        self.is_running = False
        self.next_call = time.time()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs) #Callback

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call-time.time(),self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
