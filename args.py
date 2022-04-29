#!/usr/bin/python3

class CliArgs(object):

    def __init__(self):
        self.lookup = dict()

    def register(self, option, callback):
        self.lookup[option] = callback

    def __call__(self, argv):
        for key in argv:
            if key in self.lookup:
                self.lookup[key]()
                return True
        return False

