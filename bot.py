#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)

import threading
import time
from irc_bot import IRCInterface
from wa_bot import WAInterface

def store_msg(message, file_path=None):
    if file_path is None:
        raise Exception("No file specified!")
    text = message.serialize() + "\n"
    with open(file_path, "a") as log:
        log.write(text)

    
class Bot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.must_run = False
        self.irc_i = IRCInterface("irc.freenode.net", 6667, "my_bot", "#sample_room", self.irc_msg_received, self.stop)
        self.wa_i = WAInterface("34555555125", "", self.wa_msg_received, self.stop)
    def run(self):
        self.must_run = True
        self.irc_i.start()
        self.wa_i.start()
        while not self.wa_i.connected or not self.irc_i.connected:
            if not self.must_run:
                self.irc_i.stop()
                self.wa_i.stop()
                return
            time.sleep(0.2)
        self.irc_i.send("#sample_room", "test")
        print "All connected!"

        while self.must_run:
            time.sleep(0.5)

        self.irc_i.stop()
        self.wa_i.stop()
    def stop(self):
        self.must_run = False

    def irc_msg_received(self, message):
        store_msg(message, "/tmp/log.txt")
        print " >>> Received IRC message: %s" %message
        msg = "<%s> %s" %(message.nick, message.msg)
        if message.chan == "#sample_room":
            self.wa_i.send("34555555373", "%s" %msg)

    def wa_msg_received(self, message):
        store_msg(message, "/tmp/log.txt")
        print " >>> Received WA message: %s" %message
        msg = "<%s> %s" %(message.nick, message.msg)
        if message.chan == "34555555125":
            self.irc_i.send("#sample_room", "%s" %msg)




print "Program started"
b = Bot()
try:
    b.run()
except KeyboardInterrupt:
    print "User wants to stop"
print "Program finished"
