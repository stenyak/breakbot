#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading
from datetime import datetime
import time
from log import info, error
from catch_them_all import catch_them_all
from Queue import Queue

from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from message import Message

import binascii

class Handler(DefaultCommandHandler):
    # Handle messages (the PRIVMSG command, note lower case)
    @catch_them_all
    def privmsg(self, nick_full, chan, msg):
        try:
            msg = unicode(msg, "utf-8")
        except UnicodeDecodeError:
            try:
                msg = unicode(msg, "latin-1")
            except UnicodeDecodeError:
                hexa = binascii.hexlify(msg)
                error("Could not decode message: binascii.unhexlify(\"%s\")" %hexa)
                raise
        m = Message("irc", nick_full, chan, msg)
        self.irc_interface.msg_handler(m)
    def set_irc_interface(self, irc_interface):
        self.irc_interface = irc_interface
    @catch_them_all
    def ping(self, prefix, server):
        DefaultCommandHandler.ping(self, prefix, server)
        self.irc_interface.ping()
    @catch_them_all
    def join(self, nick_full, channel):
        self.irc_interface.joined(channel)
    @catch_them_all
    def part(self, nick_full, channel):
        self.irc_interface.parted(channel)
    @catch_them_all
    def kick(self, kicker, channel, nick, reason):
        self.irc_interface.parted(channel)

class IRCInterface(threading.Thread):
    def __init__(self, server, port, nick, channels, msg_handler, stopped_handler):
        threading.Thread.__init__(self)
        self.must_run = True
        self.connected = False
        self.pinged = False
        self.msg_handler = msg_handler
        self.stopped_handler = stopped_handler
        self.nick = nick
        self.host = server
        self.port = port
        self.channels = channels
        self.send_queue = Queue()
        self.channels_joined = {}
        for c in self.channels:
            self.channels_joined[c] = False
        self.cli = IRCClient(Handler, host=self.host, port=self.port, nick=self.nick, connect_cb=self.connect_callback)
        self.cli.command_handler.set_irc_interface(self)
    @catch_them_all
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
    def parted(self, channel):
        self.channels_joined[channel] = False
        info("Left channel %s" %channel)
        if self.must_run:
            self.join_channels()
    def ping(self):
        self.pinged = True
    def connect(self):
        def wait_for_possible_ping(timeout):
            """ Some IRC servers won't allow joining channels until you've replied to a PING.
                We don't know in advance which servers PING and which don't, so we wait for `timeout` seconds before assuming it's the kind of server that doesn't PING. """
            start = datetime.now()
            while not self.pinged:
                if (datetime.now() - start).seconds > timeout:
                    break # server probably will never ping us, so just go on with our life
                if not self.must_run:
                    raise Exception("Stopped while waiting for IRC server ping")
                try:
                    self.conn.next()
                except Exception, e:
                    error("Problems while waiting for IRC server ping: %s" %e)
                    self.stop()
                    self.disconnected()
        self.server_connected = False
        self.conn = self.cli.connect()
        while not self.server_connected:
            if not self.must_run:
                raise Exception("Stopped while waiting for IRC connection")
            try:
                self.conn.next()
            except Exception, e:
                error("Problems while connecting to IRC server: %s" %e)
                self.stop()
                self.disconnected()
        wait_for_possible_ping(timeout=2)
    def next(self):
        try:
            self.conn.next()
        except Exception, e:
            time.sleep(0.05)
            error("Couldn't process connection: %s" %e)
            del self.conn
            self.connect()
    def join_channels(self):
        info("Joining channels: %s" %(", ".join(self.channels)))
        for c in self.channels:
            if not c in self.channels_joined or self.channels_joined[c] == False:
                self.cli.send("JOIN", c)
            while self.pending_channels():
                if not self.must_run:
                    raise Exception("Stopped while waiting to join channels")
                self.conn.next()
    @catch_them_all
    def run(self):
        self.must_run = True
        self.connect()
        self.join_channels()
        while not self.pending_channels():
            if not self.must_run:
                raise Exception("Stopped while waiting to join channels")
            self.next()
        self.connected = True
        info("Connected IRC client (%s@%s:%s)" %(self.nick, self.host, self.port))
        while self.must_run:
            self.next()
            time.sleep(0.1)
            if not self.send_queue.empty():
                text = self.send_queue.get()
                info((" >>> IRC %s" %text).encode("utf-8"))
                self.cli.send(text)
                time.sleep(0.5) #throttle message sending in order to avoid excess flood kick
        self.cli.send("QUIT :breakbot out")
        self.disconnected()
    def disconnected(self):
        info("Disconnected IRC client (%s@%s:%s)" %(self.nick, self.host, self.port))
        self.connected = False
        del self.conn
        self.stopped_handler()
        self.must_run = False
    def stop(self):
        self.must_run = False
    def send(self, channel, text):
        info((" ->- IRC %s: %s" %(channel, text)).encode("utf-8"))
        msg = "PRIVMSG %s :%s" %(channel, text)
        self.send_queue.put(msg)
    def wait_connected(self):
        while not self.connected:
            if not self.must_run:
                raise Exception("Stopped while waiting to connect")
            time.sleep(0.1)
