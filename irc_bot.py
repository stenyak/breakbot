#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from message import Message

        
class Handler(DefaultCommandHandler):
    def log_msg(self, message, file_path=None):
        if file_path is None:
            raise Exception("No file specified!")
        print ("Logging: %s" %message)
        text = message.serialize()
        with open(file_path, "a") as log:
            log.write(text)
        
    # Handle messages (the PRIVMSG command, note lower case)
    def privmsg(self, nick_full, chan, msg):
        m = Message(nick_full, chan, msg)
        self.log_msg(m, "/tmp/log.txt")

host = "irc.freenode.net"
port = 6667
nick = "my_bot"
cli = IRCClient(Handler, host=host, port=port, nick=nick)

conn = cli.connect()
print ""
print ""
print "===================================="
print "%s connected to %s:%s" %(nick, host, port)
while True:
    conn.next()
