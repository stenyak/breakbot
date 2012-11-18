#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)

import threading
import time
from irc_bot import IRCInterface
from wa_bot import WAInterface
from log import info, error

def store_msg(message, file_path=None):
    if file_path is None:
        raise Exception("No file specified!")
    text = message.serialize() + "\n"
    with open(file_path, "a") as log:
        log.write(text.encode("utf-8"))
def channels_from_contacts(contacts):
    channels = []
    for k,v in contacts.items():
        if v.startswith("#"):
            channels.append(v)
    channels.append("#botdebug")
    return channels
    
class Bot(threading.Thread):
    def __init__(self, wa_phone, wa_identifier, contacts, irc_server, irc_port):
        threading.Thread.__init__(self)
        self.must_run = True
        self.irc_server = irc_server
        self.irc_port = irc_port
        self.wa_phone = wa_phone
        irc_nick = contacts[wa_phone]
        self.irc_nick = irc_nick
        self.wa_identifier = wa_identifier
        self.contacts = contacts
        self.irc_i = IRCInterface(self.irc_server, self.irc_port, self.irc_nick, channels_from_contacts(self.contacts), self.irc_msg_received, self.stop)
        self.wa_i = WAInterface(self.wa_phone, self.wa_identifier, self.wa_msg_received, self.stop)
    def run(self):
        self.must_run = True
        try:
            info("Starting IRC")
            self.irc_i.start()
            info("Waiting for IRC")
            self.irc_i.wait_connected()
            info("Starting WA")
            self.wa_i.start()
            info("Waiting for WA")
            self.wa_i.wait_connected()
            info("Main loop pretty much finished")
        except:
            error("Problem while running bot")
            self.stop()
    def stop(self):
        info("Stop instructed, about to stop main loop")
        self.must_run = False
        self.irc_i.stop()
        self.wa_i.stop()

    def get_group_from_chan(self, contacts, irc_channel):
        for k,v in contacts.items():
            if v == irc_channel:
                return k
        raise Exception("Channel not found in contact list")

    def irc_msg_received(self, message):
        store_msg(message, "/tmp/log.txt")
        info(" <<< Received IRC message: %s" %message)

        msg = "<%s> %s" %(message.get_nick(), message.msg)
        try:
            group = self.get_group_from_chan(self.contacts, message.chan)
            self.wa_i.send(group, msg)
        except:
            info("Cannot send message to channel %s" %message.chan)


    def wa_msg_received(self, message):
        store_msg(message, "/tmp/log.txt")
        info(" <<< Received WA message: %s" %message)
        if message.chan == self.wa_phone:
            #private message
            if message.target is None:
                # directed to bot itself
                nick = self.contacts[message.get_nick()]
                msg = "<%s> %s" %(nick, message.msg)
                self.irc_i.send("person1", message.msg)  #TODO: lookup human IRC nick
            else:
                # directed to someone
                try:
                    phone = message.get_nick()
                    nick = self.contacts[phone]
                    target = self.get_group_from_chan(self.contacts, message.target)
                    msg = "<%s> %s" %(target, message.msg)
                    self.irc_i.send(target, msg)  #TODO: lookup human IRC nick
                except:
                    error("Couldn't relay directed WA msg to IRC")
        else:
            #group message
            try:
                msg = "<%s> %s" %(self.contacts[message.get_nick()], message.msg)
            except:
                error("Contact not recognized")
                msg = "<%s> %s" %(message.get_nick(), message.msg)
            try:
                self.irc_i.send(self.contacts[message.chan], msg)
            except:
                error("Channel %s not recognized" %(message.chan))

import json
with open("config.json", "r") as f:
    config = json.loads(f.read())
contacts = config["contacts"]
cfg = config["config"]

info("Contact list: %s" %contacts)
with open("config.json.bak", "w") as f:
    json.dump(config, f, indent=4)

info("Program started")
b = Bot(cfg["wa_phone"], cfg["wa_id"], contacts, cfg["irc_server_name"], int(cfg["irc_server_port"]))
try:
    b.start()
    while b.must_run:
        time.sleep(0.5)
except KeyboardInterrupt:
    error("User wants to stop")
finally:
    b.stop()
info("Program finished")
