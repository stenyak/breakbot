#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import threading
from message import Message
from timestamp import Timestamp
from catch_them_all import catch_them_all

import base64
from Yowsup.connectionmanager import YowsupConnectionManager
import time
from log import info, error

class WAInterface(threading.Thread):
    def __init__(self, username, password, msg_handler, stopped_handler):
        threading.Thread.__init__(self)
        self.connected = False
        self.must_run = True
        self.msg_handler = msg_handler
        self.stopped_handler = stopped_handler
        self.username = username
        self.password = base64.b64decode(password)
        self.cm = YowsupConnectionManager()
        self.cm.setAutoPong(True)
        self.signalsInterface = self.cm.getSignalsInterface()
        self.methodsInterface = self.cm.getMethodsInterface()
        self.signalsInterface.registerListener("notification_groupPictureUpdated", self.onGroup_PictureUpdated)
        self.signalsInterface.registerListener("group_gotPicture", self.onGroup_PictureGot)
        self.signalsInterface.registerListener("group_imageReceived", self.onGroup_ImageReceived)
        self.signalsInterface.registerListener("image_received", self.onImageReceived)
        self.signalsInterface.registerListener("group_videoReceived", self.onGroup_VideoReceived)
        self.signalsInterface.registerListener("videoimage_received", self.onVideoReceived)
        self.signalsInterface.registerListener("message_received", self.onMessageReceived)
        self.signalsInterface.registerListener("group_messageReceived", self.onGroup_MessageReceived)
        self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
        self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
        self.signalsInterface.registerListener("disconnected", self.onDisconnected)
        self.signalsInterface.registerListener("receipt_messageSent", self.onMessageSent)
        self.signalsInterface.registerListener("receipt_messageDelivered", self.onMessageDelivered)
        self.signalsInterface.registerListener("ping", self.onPing)
    @catch_them_all
    def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName):
        message = Message(kind="wa", nick_full=jid, chan=self.username, msg=messageContent)
        message.time = Timestamp(ms_int = timestamp*1000)
        self.msg_handler(message)
        sendReceipts = True
        if wantsReceipt and sendReceipts:
            self.wait_connected()
            self.methodsInterface.call("message_ack", (jid, messageId))
    @catch_them_all
    def onImageReceived(self, messageId, jid, preview, url, size, receiptRequested):
        messageContent = unicode("[ image: %s ]"%url, "utf-8")
        message = Message(kind="wa", nick_full=jid, chan=self.username, msg=messageContent)
        self.msg_handler(message)
        sendReceipts = True
        if receiptRequested and sendReceipts:
            self.wait_connected()
            self.methodsInterface.call("message_ack", (jid, messageId))
    @catch_them_all
    def onGroup_PictureUpdated(self, jid, author, timestamp, messageId, pictureId, receiptRequested):
        self.methodsInterface.call("group_getPicture", (jid,))
        sendReceipts = True
        if receiptRequested and sendReceipts:
            self.wait_connected()
            self.methodsInterface.call("message_ack", (jid, messageId))
    @catch_them_all
    def onGroup_PictureGot(self, jid, filePath):
        #TODO: upload filePath to services like imgur (or even upload as whatsapp picture, hah!) instead of displaying local file path here:
        messageContent = unicode("[ group picture: %s ]"%filePath, "utf-8")
        message = Message(kind="wa", nick_full="unknown", chan=jid, msg=messageContent)
        self.msg_handler(message)
    @catch_them_all
    def onGroup_ImageReceived(self, messageId, jid, author, preview, url, size, receiptRequested):
        messageContent = unicode("[ image: %s ]"%url, "utf-8")
        message = Message(kind="wa", nick_full=author, chan=jid, msg=messageContent)
        self.msg_handler(message)
        sendReceipts = True
        if receiptRequested and sendReceipts:
            self.wait_connected()
            self.methodsInterface.call("message_ack", (jid, messageId))
    @catch_them_all
    def onVideoReceived(self, messageId, jid, preview, url, size, receiptRequested):
        messageContent = unicode("[ video: %s ]"%url, "utf-8")
        message = Message(kind="wa", nick_full=jid, chan=self.username, msg=messageContent)
        self.msg_handler(message)
        sendReceipts = True
        if receiptRequested and sendReceipts:
            self.wait_connected()
            self.methodsInterface.call("message_ack", (jid, messageId))
    @catch_them_all
    def onGroup_VideoReceived(self, messageId, jid, author, preview, url, size, receiptRequested):
        messageContent = unicode("[ video: %s ]"%url, "utf-8")
        message = Message(kind="wa", nick_full=author, chan=jid, msg=messageContent)
        self.msg_handler(message)
        sendReceipts = True
        if receiptRequested and sendReceipts:
            self.wait_connected()
            self.methodsInterface.call("message_ack", (jid, messageId))
    @catch_them_all
    def onGroup_MessageReceived(self, messageId, jid, author, messageContent, timestamp, wantsReceipt, pushName):
        message = Message(kind="wa", nick_full=author, chan=jid, msg=messageContent)
        message.time = Timestamp(ms_int = timestamp*1000)
        self.msg_handler(message)
        sendReceipts = True
        if wantsReceipt and sendReceipts:
            self.wait_connected()
            self.methodsInterface.call("message_ack", (jid, messageId))

    @catch_them_all
    def run(self):
        try:
            self.must_run = True
            self.methodsInterface.call("auth_login", (self.username, self.password))
            self.wait_connected()
            while self.must_run:
                if not self.connected:
                    self.methodsInterface.call("auth_login", (self.username, self.password))
                time.sleep(0.5)
                #raw_input()
        finally:
            info("Main loop closing")
            self.connected = False
            self.stopped_handler()
            self.must_run = False
    def stop(self):
        self.must_run = False
    def send(self, target, text):
        self.wait_connected()
        self.methodsInterface.call("message_send", (target, text.encode("utf-8")))
        info((" >>> WA %s: %s" %(target, text)).encode("utf-8"))
    @catch_them_all
    def onAuthSuccess(self, username):
        info("Connected WA client (%s)" %username)
        self.connected = True
        self.methodsInterface.call("ready")
    @catch_them_all
    def onAuthFailed(self, username, reason):
        info("Auth Failed: %s" %reason)
        self.connected = False
    @catch_them_all
    def onDisconnected(self, reason):
        info("Disconnected WA client (%s): %s" %(self.username, reason))
        self.connected = False
    @catch_them_all
    def onMessageSent(self, jid, messageId):
        info("Message successfully sent to %s" % jid)
    @catch_them_all
    def onMessageDelivered(self, jid, messageId):
        info("Message successfully delivered to %s" %jid)
        self.wait_connected()
        self.methodsInterface.call("delivered_ack", (jid, messageId))
    @catch_them_all
    def onPing(self, pingId):
        info("Pong! (%s)" %pingId)
        self.wait_connected()
        self.methodsInterface.call("pong", (pingId,))
    def wait_connected(self):
        while not self.connected:
            if not self.must_run:
                raise Exception("bot does not intend to connect")
            time.sleep(0.1)
