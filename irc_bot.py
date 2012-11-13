#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading
import time
from log import Log
logger = Log("IRC")

import traceback
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from message import Message

class Handler(DefaultCommandHandler):
    # Handle messages (the PRIVMSG command, note lower case)
    def privmsg(self, nick_full, chan, msg):
        m = Message("irc", nick_full, chan, msg)
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
        self.connected = False
        self.msg_handler = msg_handler
        self.stopped_handler = stopped_handler
        self.nick = nick
        self.host = server
        self.port = port
        self.channels = channels
        self.channels_joined = {}
        for c in self.channels:
            self.channels_joined[c] = False
        self.cli = IRCClient(Handler, host=self.host, port=self.port, nick=self.nick, connect_cb=self.connect_callback)
        self.cli.command_handler.set_irc_interface(self)
    def connect_callback(self, cli):
        self.server_connected = True
    def pending_channels(self):
        result = True
        for k,v in self.channels_joined.items():
            if not v:
                result = False
                break
        return result
    def joined(self, channel):
        self.channels_joined[channel] = True
        logger.info("Joined channel %s" %channel)
    def connect(self):
        logger.info("Connecting to server")
        self.server_connected = False
        conn = self.cli.connect()
        while not self.server_connected:
            if not self.must_run:
                raise Exception("Must stop")
            conn.next()
        logger.info("Connected to server")
        return conn
    def join_channels(self, conn):
        for c in self.channels:
            logger.info("Joining channel %s" %c)
            self.cli.send("JOIN", c)
            while self.pending_channels():
                if not self.must_run:
                    raise Exception("Must stop")
                conn.next()

    def run(self):
        try:
            self.must_run = True
            logger.info("%s connecting to %s:%s" %(self.nick, self.host, self.port))
            conn = self.connect()
            self.join_channels(conn)
            while not self.pending_channels():
                if not self.must_run:
                    raise Exception("Must stop")
                conn.next()
            self.connected = True
            logger.info("%s connected to %s:%s" %(self.nick, self.host, self.port))
            while self.must_run:
                conn.next()
            self.cli.send("QUIT :a la mieeerrrrda")
            logger.info("%s disconnected from %s:%s" %(self.nick, self.host, self.port))
            self.connected = False
            self.stopped_handler()
            self.must_run = False
        except:
            logger.info("Error in main loop: %s" %traceback.format_exc())
    def stop(self):
        self.must_run = False
    def send(self, channel, text):
        logger.info(" >>> Sending IRC message: %s: %s" %(channel, text))
        msg = "PRIVMSG %s :%s" %(channel, text)
        self.cli.send(msg)
    def wait_connected(self):
        while not self.connected:
            if not self.must_run:
                raise Exception("IRC: bot does not intend to connect")
            time.sleep(0.1)
