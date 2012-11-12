#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)

import time
from irc_bot import IRCInterface
#from wa_bot import WAInterface

def store_msg(message, file_path=None):
    if file_path is None:
        raise Exception("No file specified!")
    text = message.serialize()
    with open(file_path, "a") as log:
        log.write(text)

def irc_msg_received(message):
    store_msg(message, "/tmp/log.txt")
    print "Received irc message: %s" %message

def wa_msg_received(message):
    print "Received wa message: %s" %message

bot_running = False
def bot_stopped():
    bot_running = False
    
def main():
    irc_i = IRCInterface("irc.freenode.net", 6667, "my_bot", ["#sample_room"], irc_msg_received, bot_stopped)
    bot_running = True
    irc_i.start()
    seconds = 0
    try:
        while bot_running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print "User wants to stop"
    irc_i.stop()


print "Program started"
main()
print "Program finished"
