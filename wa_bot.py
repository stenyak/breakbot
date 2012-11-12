#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading

from yowsup.Examples import ListenerClient as ListenerClient
from yowsup.Examples.CmdClient import WhatsappCmdClient as WhatsappCmdClient
from yowsup.Yowsup.Tools.utilities import Utilities
import os
import datetime
import time

class WAInterface(threading.Thread):
    def __init__(self, server, port, nick, handler):
        threading.Thread.__init__(self)
        self.must_run = False
        self.handler = handler
        DEFAULT_CONFIG = os.path.expanduser("~")+"/.yowsup/auth"
        def getCredentials(config = DEFAULT_CONFIG):
            if os.path.isfile(config):
                f = open(config)
                l = f.readline().strip()
                auth = l.split(":", 1)
                if len(auth) == 2:
                    return auth
                return 0
        credentials = getCredentials(DEFAULT_CONFIG)
        username, identity = credentials
        password = Utilities.getPassword(identity)
        wa = WhatsappCmdClient(True, False)
        wa.signalsInterface.registerListener("message_received", onMessageReceived)
        wa.methodsInterface.call("auth_login", (username, password))
    def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt):
        try:
            print "message received: %s" % messageContent
            formattedDate = datetime.datetime.fromtimestamp(timestamp/1000).strftime('%d-%m-%Y %H:%M')
            print "%s:%s"%(jid, formattedDate, messageContent)
        except Exception,e:
            print "Shit happened: %s" %e

    def run(self):
        self.must_run = True
        while self.must_run:
            time.sleep(0.5)
    def stop(self):
        self.must_run = False
