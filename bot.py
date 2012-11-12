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
def channels_from_groups(groups):
    channels = []
    for k,v in groups.items():
        if v.startswith("#"):
            channels.append(v)
    return channels
    
class Bot(threading.Thread):
    def __init__(self, wa_phone, wa_identifier, groups, irc_server, irc_port):
        threading.Thread.__init__(self)
        self.must_run = False
        self.irc_server = irc_server
        self.irc_port = irc_port
        self.wa_phone = wa_phone
        irc_nick = groups[wa_phone]
        self.irc_nick = irc_nick
        self.wa_identifier = wa_identifier
        self.groups = groups
        self.irc_i = IRCInterface(self.irc_server, self.irc_port, self.irc_nick, channels_from_groups(self.groups), self.irc_msg_received, self.stop)
        self.wa_i = WAInterface(self.wa_phone, self.wa_identifier, self.wa_msg_received, self.stop)
    def run(self):
        self.must_run = True
        self.irc_i.start()
        self.wa_i.start()
        while not self.wa_i.connected or not self.irc_i.connected:
            if not self.must_run:
                self.irc_i.stop()
                self.wa_i.stop()
                return
            time.sleep(0.5)
        print "All connected!"

        while self.must_run:
            time.sleep(0.5)

        self.irc_i.stop()
        self.wa_i.stop()
    def stop(self):
        self.must_run = False

    def irc_msg_received(self, message):
        store_msg(message, "/tmp/log.txt")
        print " <<< Received IRC message: %s" %message

        msg = "<%s> %s" %(message.get_nick(), message.msg)
        if message.chan == self.irc_channel:
            self.wa_i.send(self.wa_chat, "%s" %msg)
            #self.wa_i.send("34555555373@s.whatsapp.net", "%s" %msg)

    def wa_msg_received(self, message):
        store_msg(message, "/tmp/log.txt")
        print " <<< Received WA message: %s" %message
        try:
            nick = message.get_nick()
            msg = "<%s> %s" %(self.groups[message.get_nick()], message.msg)
            self.irc_i.send(self.groups[message.chan], "%s" %msg)
        except Exception,e:
            print "Not sending message: %s" %e


groups = {
    "34555555125": "my_bot"
   ,"34555555373": "person1"
   ,"34555555530": "person2"
   ,"34555555373-1352752705@g.us": "#sample_room"
   ,"34555555530-1321985629@g.us": "#sample_room2"
}
print "%s" %groups

print "Program started"
b = Bot("34555555125", "", groups, "irc.freenode.net", 6667)
try:
    b.run()
except KeyboardInterrupt:
    print "User wants to stop"
print "Program finished"
