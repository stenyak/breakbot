#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import unittest
from message import Message, split_nick, sed
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

    def test_sed(self):
        self.assertEquals(sed("foobar", "(foo)"), "foo")
        self.assertEquals(sed("bar 123 baz", r"bar (\d+) baz"), "123")
        self.assertEquals(sed("bar 123 baz", r"bar (\d+) "),    "123")
        self.assertEquals(sed("bar 123 baz", r"^bar (\d+) "),   "123")
        self.assertEquals(sed("bar 123 baz", r"^.* (\d+)"),     "123")
        self.assertEquals(sed("bar 123 baz", r"^.* (\d+).*$"),  "123")
        self.assertEquals(sed("  123   \t", r"^\s*(\d*)\s*$"),  "123")
        self.assertEquals(sed("  foo123bar   ", r"^\s*([a-z0-9]*)\s*$"),    "foo123bar")
        self.assertEquals(sed("  foo123BAR   ", r"^\s*([a-zA-Z0-9]*)\s*$"), "foo123BAR")
        self.assertEquals(sed("  foo123ba+r   ", r"^\s*([a-z0-9+]*)\s*$"),  "foo123ba+r")
        self.assertEquals(sed("  foo123ba+r   ", r"^\s*([a-z0-9+]*)\s*$"),  "foo123ba+r")
        self.assertEquals(sed("  foo   ", r"\s*([a-z]*)\s*"), "foo")
        self.assertEquals(sed("  foo   ", r"\s(\w+)\s"), "foo")
        self.assertEquals(sed("  foo   ", r"\s*\s(\w+)\s*"), "foo")
        self.assertEquals(sed("foo:hey", r"\s*(\w+)\s*:"), "foo")
        self.assertEquals(sed(" foo:hey", r"\s*(\w+)\s*:"), "foo")
        self.assertEquals(sed("foo :hey", r"\s*(\w+)\s*:"), "foo")
        self.assertEquals(sed("foo:hey ", r"\s*(\w+)\s*:"), "foo")
        self.assertEquals(sed(" foo : hey ", r"\s*(\w+)\s*:"), "foo")
        self.assertEquals(sed("  foo  :  hey  ", r"\s*(\w+)\s*:"), "foo")
        self.assertEquals(sed("  foo  :  hey  ", r"^\s*(\w+)\s*:"), "foo")
        self.assertEquals(sed("  foo_bar  :  hey  ", r"^\s*(\w+)\s*:"), "foo_bar")
        self.assertEquals(sed("  +34555555  :  hey  ", r"^\s*([\w0-9+]+)\s*:"), "+34555555")

    def test_split(self):
        self.assertEquals(split_nick("foo bar"), [None, "foo bar"])
        self.assertEquals(split_nick("foo:bar"), ["foo", "bar"])
        self.assertEquals(split_nick("foo:"), ["foo", ""])
        self.assertEquals(split_nick(" foo : bar "), ["foo", "bar "])
        self.assertEquals(split_nick("ftp://foobar"), [None, "ftp://foobar"])
        self.assertEquals(split_nick("ftp://foo:bar"), [None, "ftp://foo:bar"])
        self.assertEquals(split_nick("ftp://foo:bar"), [None, "ftp://foo:bar"])
        self.assertEquals(split_nick(":)"), [None, ":)"])
        self.assertEquals(split_nick("hey :)"), [None, "hey :)"])
        self.assertEquals(split_nick("foo: whats up? :)"), ["foo", "whats up? :)"])
        self.assertEquals(split_nick("foo: whats up? :("), ["foo", "whats up? :("])
        self.assertEquals(split_nick("foo: whats up? :/"), ["foo", "whats up? :/"])
        self.assertEquals(split_nick("foo: whats up? :-/"), ["foo", "whats up? :-/"])
        self.assertEquals(split_nick("foo: check this url: ftp://foo :-)"), ["foo", "check this url: ftp://foo :-)"])

if __name__ == '__main__':
    unittest.main()
