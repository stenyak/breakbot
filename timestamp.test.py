#!/usr/bin/python
# Copyright 2012 Bruno Gonzalez
# This software is released under the GNU AFFERO GENERAL PUBLIC LICENSE (see agpl-3.0.txt or www.gnu.org/licenses/agpl-3.0.html)
import unittest
from timestamp import Timestamp

class TestTimestamp(unittest.TestCase):
    def test_basic(self):
        t = Timestamp()
        self.assertTrue(t is not None)
        ms = t.ms_int()
        self.assertTrue(ms is not None)
        st = str(t)
        self.assertTrue(st is not None)

    def test_integrity(self):
        t = Timestamp()
        self.assertEqual(t.ms_int(), t.ms_int())
        self.assertEqual(str(t), str(t))

    def test_integrity2(self):
        t = Timestamp()
        t2 = Timestamp()
        self.assertNotEqual(t.ms_int(), t2.ms_int())
        t3 = Timestamp(ms_int = t.ms_int())
        self.assertEqual(t.ms_int(), t3.ms_int())

    def test_comparison(self):
        t = Timestamp()
        self.assertTrue(t == t)
        self.assertTrue(not t != t)
        self.assertTrue(not t > t)
        self.assertTrue(not t < t)
        self.assertTrue(t <= t)
        self.assertTrue(t >= t)

        t2 = Timestamp()
        self.assertTrue(not t == t2)
        self.assertTrue(t != t2)
        self.assertTrue(t < t2)
        self.assertTrue(t2 > t)
        self.assertTrue(t <= t2)
        self.assertTrue(t2 >= t)

    def test_parse(self):
        t = Timestamp(ms_int = 10)
        self.assertEqual(t.ms_int(), 10)
        self.assertEqual(str(t), "10")

        t = Timestamp(ms_str = "10")
        self.assertEqual(t.ms_int(), 10)
        self.assertEqual(str(t), "10")

        t2 = Timestamp(ms_int = 10)
        self.assertEqual(t.ms_int(), t2.ms_int())

        t3 = Timestamp(ms_str = str(t))
        self.assertEqual(t.ms_int(), t3.ms_int())


if __name__ == '__main__':
    unittest.main()
