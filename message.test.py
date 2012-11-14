#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import unittest
from message import Message
from timestamp import Timestamp

class TestMessage(unittest.TestCase):
    def test_basic(self):
        m = Message("irc", "complete_nick!foobar", "channel_name", "message contents")
        t = Timestamp()
        self.assertTrue(m.time < t)
        self.assertEquals(m.nick_full, "complete_nick!foobar")
        self.assertEquals(m.nick_full, "complete_nick!foobar")
        self.assertEquals(m.get_nick(), "complete_nick")
        self.assertEquals(m.chan, "channel_name")
        self.assertEquals(m.msg, "message contents")
        self.assertTrue(m.target is None)

    def test_target(self):
        m = Message("irc", "complete_nick!foobar", "channel_name", "BaZ: message contents")
        self.assertEquals(m.target, "BaZ")

    def test_serialize(self):
        m = Message("irc", "complete_nick!foobar", "channel_name", "BaZ: message contents", 10)
        self.assertEquals(m.serialize(), "10 @@@ irc @@@ complete_nick!foobar @@@ channel_name @@@ BaZ: message contents")
        
    def test_deserialize(self):
        m = Message("irc", "complete_nick!foobar", "channel_name", "BaZ: message contents", 10)
        m2 = Message(serialized_str=m.serialize())
        self.assertEquals(m.serialize(), m2.serialize())
        m3 = Message(serialized_str="10 @@@ irc @@@ complete_nick!foobar @@@ channel_name @@@ BaZ: message contents")
        self.assertEquals(m.serialize(), m3.serialize())

if __name__ == '__main__':
    unittest.main()
