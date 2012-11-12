#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading
from message import Message
from timestamp import Timestamp

from yowsup.Examples import ListenerClient as ListenerClient
from yowsup.Examples.CmdClient import WhatsappCmdClient as WhatsappCmdClient
from yowsup.Yowsup.Tools.utilities import Utilities
from yowsup.Yowsup.connectionmanager import YowsupConnectionManager
import os
import datetime
import time

class WAInterface(threading.Thread):
    def __init__(self, username, identity, msg_handler, stopped_handler):
        threading.Thread.__init__(self)
        self.must_run = False
        self.msg_handler = msg_handler
        self.stopped_handler = stopped_handler
        self.username = username
        self.identity = identity
    def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt):
        try:
            message = Message(self.username, jid, messageContent)
            message.time = Timestamp(ms_int = timestamp*1000)
            self.msg_handler(message)
        except Exception,e:
            print "Error while handling message: %s" %e
        wantsReceipt = False
        sendReceipts = False
        if wantsReceipt and sendReceipts:
            self.methodsInterface.call("message_ack", (jid, messageId))

    def run(self):
        self.must_run = True
        connectionManager = YowsupConnectionManager()
        connectionManager.setAutoPong(True)
        self.signalsInterface = connectionManager.getSignalsInterface()
        self.methodsInterface = connectionManager.getMethodsInterface()
        self.signalsInterface.registerListener("message_received", self.onMessageReceived)
        self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
        self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
        self.signalsInterface.registerListener("disconnected", self.onDisconnected)
        self.cm = connectionManager
        self.methodsInterface.call("auth_login", (self.username, Utilities.getPassword(self.identity)))
        while self.must_run:
            raw_input()
        self.stopped_handler()
    def stop(self):
        self.must_run = False
    def send(self, target, text):
        print " >>> Sending WA message: %s" %message
        message = ("%s@s.whatsapp.net"%target, text)
        self.wa.methodsInterface.call("message_id", message)
        print " >>> Sent!"
        print " >>> Sending WA message: %s" %message
    def onAuthSuccess(self, username):
        print "Authed %s" % username
        self.methodsInterface.call("ready")
    def onAuthFailed(self, username, err):
        print "Auth Failed!"
    def onDisconnected(self, reason):
        print "Disconnected because %s" %reason


