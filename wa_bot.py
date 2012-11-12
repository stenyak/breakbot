#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading
from message import Message
from timestamp import Timestamp

from yowsup.Examples import ListenerClient as ListenerClient
from yowsup.Examples.CmdClient import WhatsappCmdClient as WhatsappCmdClient
from yowsup.Yowsup.Tools.utilities import Utilities
import os
import datetime
import time

class WAInterface(threading.Thread):
    def __init__(self, auth_file, msg_handler, stopped_handler):
        threading.Thread.__init__(self)
        self.must_run = False
        self.msg_handler = msg_handler
        self.stopped_handler = stopped_handler
        def getCredentials(auth_file):
            if os.path.isfile(auth_file):
                f = open(auth_file)
                l = f.readline().strip()
                auth = l.split(":", 1)
                if len(auth) == 2:
                    return auth
                return 0
        credentials = getCredentials(auth_file)
        username, identity = credentials
        password = Utilities.getPassword(identity)
        self.username = username
        self.identify = identity
        self.password = password
        self.wa = WhatsappCmdClient(True, False)
        self.wa.signalsInterface.registerListener("message_received", self.onMessageReceived)
        self.signals = y.getSignalsInterface()
        self.methods = y.getMethodsInterface()
    def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt):
        try:
            message = Message(self.username, jid, messageContent)
            message.time = Timestamp(ms_int = timestamp*1000)
            self.msg_handler(message)
        except Exception,e:
            print "Error while handling message: %s" %e

    def run(self):
        self.must_run = True
        self.wa.methodsInterface.call("auth_login", (self.username, self.password))
        while self.must_run:
            time.sleep(0.5)
        self.stopped_handler()
    def stop(self):
        self.must_run = False
    def send(self, target, text):
        print " >>> Sending WA message: %s" %message
        message = ("%s@s.whatsapp.net"%target, text)
        self.wa.methodsInterface.call("message_id", message)
        print " >>> Sent!"
        print " >>> Sending WA message: %s" %message
