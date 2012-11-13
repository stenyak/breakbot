# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from timestamp import Timestamp

class Message():
    def __init__(self, kind, nick_full=None, chan=None, msg=None, time=None, serialized_str=None):
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
            self.msg = msg
            self.target = None
            try:
                split = msg.split(":", 1)
                if len(split) == 2:
                    self.target = split[0]
                    msg = split[1].lstrip()
            except IndexError:
                pass
        else:
            self.deserialize(serialized_str)
    def get_nick(self):
        if self.kind == "irc":
            return self.nick_full.split("!", 1)[0]
        if self.kind == "wa":
            return self.nick_full.split("@")[0]
        raise Exception("Couldn't parse full nick %s" %self.nick_full)
    def __str__(self):
        return "%s: %s in %s said to %s: %s" % (self.time, self.get_nick(), self.chan, self.target, self.msg)
    def serialize(self):
        return " @@@ ".join([str(self.time), self.nick_full, self.chan, self.msg])
    def deserialize(self, string):
        fields = string.split(" @@@ ")
        time = Timestamp(ms_str=fields[0])
        nick_full = fields[1]
        chan = fields[2]
        msg = fields[3]
        self.__init__(nick_full, chan, msg, time, serialized_str=None)
