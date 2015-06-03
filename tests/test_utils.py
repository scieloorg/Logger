# coding: utf-8
import unittest

from logger.utils import TimedSet, checkdatelock

from . import fixtures


class TimedSetTests(unittest.TestCase):
    def test_expiration(self):
        ts = TimedSet(expired=checkdatelock)
        ts.add('art1', '2013-05-29T00:01:01')
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        with self.assertRaises(ValueError):
            ts.add('art1', '2013-05-29T00:01:05')

        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        ts.add('art1', '2013-05-29T00:01:22')
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:22'})

    def test_expiration_custom_timeout(self):
        ts = TimedSet(expired=checkdatelock)
        ts.add('art1', '2013-05-29T00:01:01', 30)
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        with self.assertRaises(ValueError):
            ts.add('art1', '2013-05-29T00:01:031')

        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:01'})

        ts.add('art1', '2013-05-29T00:01:32')
        self.assertTrue(ts._items, {'art1': '29/May/2013:00:01:32'})