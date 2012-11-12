#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading

from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from message import Message
from oyoyo import helpers
import time

class Handler(DefaultCommandHandler):
    # Handle messages (the PRIVMSG command, note lower case)
    def privmsg(self, nick_full, chan, msg):
        m = Message(nick_full, chan, msg)
        try:
            self.irc_interface.msg_handler(m)
        except:
            pass
    def set_irc_interface(self, irc_interface):
        self.irc_interface = irc_interface
    def join(self, nick_full, channel):
        self.irc_interface.joined(channel)

class IRCInterface(threading.Thread):
    def __init__(self, server, port, nick, channels, msg_handler, stopped_handler):
        threading.Thread.__init__(self)
        self.must_run = False
        self.msg_handler = msg_handler
        self.stopped_handler = stopped_handler
        self.nick = nick
        self.host = server
        self.port = port
        self.channels = {}
        for channel in channels:
            self.channels[channel] = False
        self.connected = False
    def connect_callback(self, cli):
        self.connected = True
    def join(self, channel):
        print "Joining channel %s ..." %channel
        self.cli.send("JOIN", channel)
    def joined(self, channel):
        self.channels[channel] = True
        print "Joined channel %s" %channel
    def all_joined(self):
        result = True
        for k,v in self.channels.items():
            if v == False:
                result = False
                break
        return result
    def run(self):
        self.must_run = True
        print "IRC: %s connecting to %s:%s" %(self.nick, self.host, self.port)
        self.cli = IRCClient(Handler, host=self.host, port=self.port, nick=self.nick, connect_cb=self.connect_callback)
        self.cli.command_handler.set_irc_interface(self)
        conn = self.cli.connect()
        while not self.connected:
            if not self.must_run:
                return
            conn.next()
        for channel in self.channels:
            self.join(channel)
        while not self.all_joined():
            if not self.must_run:
                return
            conn.next()
        print "IRC: %s connected to %s:%s" %(self.nick, self.host, self.port)
        while self.must_run:
            conn.next()
        print "IRC: %s disconnected from %s:%s" %(self.nick, self.host, self.port)
        self.connected = False
        self.stopped_handler()
    def stop(self):
        self.must_run = False
