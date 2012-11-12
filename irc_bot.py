#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading

import traceback
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from message import Message

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
    def __init__(self, server, port, nick, channel, msg_handler, stopped_handler):
        threading.Thread.__init__(self)
        self.must_run = False
        self.connected = False
        self.msg_handler = msg_handler
        self.stopped_handler = stopped_handler
        self.nick = nick
        self.host = server
        self.port = port
        self.channel = channel
        self.channel_joined = False
        self.cli = IRCClient(Handler, host=self.host, port=self.port, nick=self.nick, connect_cb=self.connect_callback)
        self.cli.command_handler.set_irc_interface(self)
    def connect_callback(self, cli):
        print "Connected to IRC"
        self.server_connected = True
    def joined(self, channel):
        self.channel_joined = True
        print "Joined channel %s" %channel
    def connect(self):
        print "Connecting to server"
        self.server_connected = False
        conn = self.cli.connect()
        while not self.server_connected:
            if not self.must_run:
                raise Exception("Must stop")
            conn.next()
        print "Connected to server"
        return conn
    def join(self, conn, channel):
        print "Joining channel"
        self.cli.send("JOIN", channel)
        while not self.channel_joined:
            if not self.must_run:
                raise Exception("Must stop")
            conn.next()
        print "Joined channel"

    def run(self):
        try:
            self.must_run = True
            print "IRC: %s connecting to %s:%s" %(self.nick, self.host, self.port)
            conn = self.connect()
            self.join(conn, self.channel)
            self.connected = True
            print "IRC: %s connected to %s:%s" %(self.nick, self.host, self.port)
            while self.must_run:
                conn.next()
            self.cli.send("QUIT :a la mieeerrrrda")
            print "IRC: %s disconnected from %s:%s" %(self.nick, self.host, self.port)
            self.connected = False
            self.stopped_handler()
        except Exception,e:
            print traceback.format_exc()
    def stop(self):
        self.must_run = False
    def send(self, channel, text):
        print " >>> Sending IRC message: %s: %s" %(channel, text)
        msg = "PRIVMSG %s :%s" %(channel, text)
        self.cli.send(msg)
        print " >>> Sent    IRC message: %s: %s" %(channel, text)
