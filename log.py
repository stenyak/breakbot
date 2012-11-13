# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from timestamp import Timestamp
class Log():
    def __init__(self, name):
        self.name = name
    def info(self, text):
        print "%s: %s: %s" %(Timestamp().to_human_str(), self.name, text)
