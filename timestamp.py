# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import time

class Timestamp():
    def __init__(self, ms_str = None, ms_int = None):
        if ms_str is not None:
            self.time = long(ms_str) / 1000. / 1000.
        elif ms_int is not None:
            self.time = ms_int / 1000. / 1000.
        else:
            self.time = time.time()  #long
    def __str__(self):
        return str(self.ms_int())
    def ms_int(self):
        return int(round(self.time * 1000 * 1000))
    def __eq__(self, other):
        return self.time == other.time
    def __ne__(self,other):
        return self.time != other.time
    def __lt__(self, other):
        return self.time < other.time
    def __gt__(self, other):
        return self.time > other.time
    def __le__(self, other):
        return self.time <= other.time
    def __ge__(self, other):
        return self.time >= other.time
        
