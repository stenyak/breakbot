#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler

class MyHandler(DefaultCommandHandler):
    # Handle messages (the PRIVMSG command, note lower case)
    def privmsg(self, nick, chan, msg):
        target = None
        try:
            split = msg.split(":", 1)
            msg = split[1].lstrip()
            target = split[0]
        except IndexError:
            pass
        print "%s in %s said to %s: %s" % (nick, chan, target, msg)

host = "irc.freenode.net"
port = 6667
nick = "my_bot"
cli = IRCClient(MyHandler, host=host, port=port, nick=nick)

conn = cli.connect()
print ""
print ""
print "===================================="
print "%s connected to %s:%s" %(nick, host, port)
while True:
    conn.next()
