# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from timestamp import Timestamp
import re

def sed(text, regexp):
    m = re.search(regexp, text)
    if m:
        return m.groups()[0]
    else:
        return None

def split_nick(text):
    target = sed(text, r"^\s*([\w0-9+]+)\s*:\s*.*")
    if target in (None, "ftp", "ssh", "http","https","image"):
        return [None, text]
    msg = sed(text, r"^\s*[\w0-9+]+\s*:\s*(.*)")
    if msg.startswith((")", "(", "/", "-")):
        return [None, text]
    return [target, msg]

class Message():
    def __init__(self, kind=None, nick_full=None, chan=None, msg=None, time=None, serialized_str=None):
        if serialized_str is None:
            if time is None:
                self.time = Timestamp()
            else:
                self.time = time
            if kind not in ["wa", "irc"]:
                raise Exception("Message kind must be 'wa' or 'irc'")
            self.kind = kind
            self.nick_full = nick_full
            self.chan = chan
            self.target, self.msg = split_nick(msg)
        else:
            self.deserialize(serialized_str)
    def get_nick(self):
        if self.kind == "irc":
            return self.nick_full.split("!", 1)[0]
        if self.kind == "wa":
            return self.nick_full.split("@")[0]
        raise Exception("Couldn't parse full nick %s" %self.nick_full)
    def __str__(self):
        return ("%s: %s in %s said to %s: %s" % (self.time, self.get_nick(), self.chan, self.target, self.msg)).encode("utf-8")
    def serialize(self):
        return " @@@ ".join([str(self.time), self.kind, self.nick_full, self.chan, self.msg if self.target is None else "%s: %s"%(self.target, self.msg)])
    def deserialize(self, string):
        fields = string.split(" @@@ ")
        time = Timestamp(ms_str=fields[0])
        kind = fields[1]
        nick_full = fields[2]
        chan = fields[3]
        msg = fields[4]
        self.__init__(kind, nick_full, chan, msg, time, serialized_str=None)
