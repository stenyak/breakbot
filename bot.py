#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)

import threading
import time
from irc_bot import IRCInterface
from wa_bot import WAInterface
from log import info, error, warning
from catch_them_all import catch_them_all
import traceback

def store_msg(message, file_path=None):
    if file_path is None:
        raise Exception("No file specified!")
    try:
        text = message.serialize() + "\n"
        with open(file_path, "a") as log:
            log.write(text.encode("utf-8"))
    except:
        error("Couldn't write message to log")

def channels_from_contacts(contacts):
    channels = []
    for k,v in contacts.items():
        if v.startswith("#"):
            channels.append(v)
    return channels

class Bot(threading.Thread):
    def __init__(self, wa_phone, wa_password, contacts, irc_server, irc_port, owner_nick, log_file):
        threading.Thread.__init__(self)
        self.must_run = True
        self.irc_server = irc_server
        self.irc_port = irc_port
        self.owner_nick = owner_nick
        self.wa_phone = wa_phone
        self.log_file = log_file
        irc_nick = contacts[wa_phone]
        self.irc_nick = irc_nick
        self.wa_password = wa_password
        self.contacts = contacts
        self.irc_i = IRCInterface(self.irc_server, self.irc_port, self.irc_nick, channels_from_contacts(self.contacts), self.irc_msg_received, self.stop)
        self.wa_i = WAInterface(self.wa_phone, self.wa_password, self.wa_msg_received, self.stop)
    @catch_them_all
    def run(self):
        try:
            self.must_run = True
            info("Connecting IRC client (%s@%s:%s)" %(self.irc_nick, self.irc_server, self.irc_port))
            self.irc_i.start()
            self.irc_i.wait_connected()
            info("Connecting WA client (%s)" %self.wa_phone)
            self.wa_i.start()
            self.wa_i.wait_connected()
            info("Bot ready.")
        except:
            info("Main loop closing")
            self.stop()
    def stop(self):
        info("Bot stopping...")
        self.must_run = False
        self.irc_i.stop()
        self.wa_i.stop()

    def get_wa_id_from_name(self, contacts, name):
        for k,v in contacts.items():
            if v.lower() == name.lower():
                return k
        raise Exception("Channel not found in contact list")

    @catch_them_all
    def irc_msg_received(self, message):
        store_msg(message, self.log_file)
        info(" <<< IRC %s" %message)

        if message.chan == self.irc_nick:
            if message.target is None:
                raise Exception("Target not specified. Please prefix you private messages with a nickname (e.g. 'person1: hello') or phone number (e.g. '+34555555373: hello')")
            try:
                wa_target = self.contacts[message.target] #try by phone
            except KeyError:
                wa_target = self.get_wa_id_from_name(self.contacts, message.target) #try by nick
            wa_target += "@s.whatsapp.net"
            msg = "<%s> %s" %(message.get_nick(), message.msg.split(":", 1)[1])
            self.wa_i.send(wa_target, msg)
        else:
            msg = "<%s> %s" %(message.get_nick(), message.msg)
            try:
                group = self.get_wa_id_from_name(self.contacts, message.chan)
                self.wa_i.send(group, msg)
            except Exception, e:
                error("Cannot send message to channel %s: %s" %(message.chan, e))

    @catch_them_all
    def wa_msg_received(self, message):
        store_msg(message, self.log_file)
        lines = message.msg.strip().split("\n") #split multiline messages
        info(" <<< WA %s" %message)
        if message.chan == self.wa_phone:
            #private message
            if message.target is None:
                # directed to bot itself
                nick = self.contacts[message.get_nick()]
                irc_target = self.contacts[message.nick_full.split("@")[0]]
                for line in lines:
                    irc_msg = "<%s> %s" %(nick, line)
                    self.irc_i.send(self.owner_nick, irc_msg)
            else:
                # directed to someone
                try:
                    phone = message.get_nick()
                    nick = self.contacts[phone]
                    target = self.get_wa_id_from_name(self.contacts, message.target)
                    for line in lines:
                        msg = "<%s> %s" %(target, line)
                        self.irc_i.send(target, msg)
                except:
                    error("Couldn't relay directed WA msg to IRC")
        else:
            #group message
            for line in lines:
                try:
                    msg = "<%s> %s" %(self.contacts[message.get_nick()], line)
                except:
                    warning("Contact not recognized")
                    msg = "<%s> %s" %(message.get_nick(), line)
                try:
                    self.irc_i.send(self.contacts[message.chan], msg)
                except:
                    warning("Channel %s not recognized" %(message.chan))

import json
with open("config.json", "r") as f:
    config = json.loads(f.read())
contacts = config["contacts"]
cfg = config["config"]

info("%s contacts loaded from configuration file" %len(contacts))
with open("config.json.bak", "w") as f:
    json.dump(config, f, indent=4)

b = Bot(cfg["wa_phone"], cfg["wa_password"], contacts, cfg["irc_server_name"], int(cfg["irc_server_port"]), cfg["bot_owner_nick"], cfg["log_file"])
try:
    b.start()
    while b.must_run:
        time.sleep(0.5)
except KeyboardInterrupt:
    print ""
    warning("User wants to stop")
finally:
    b.stop()
info("Bot stopped.")
