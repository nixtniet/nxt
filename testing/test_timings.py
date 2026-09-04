# This file is placed in the Public Domain.


"time related"


import unittest


from nxt.defines import Time


class TestTime(unittest.TestCase):

    def test_times(self):
        self.assertTrue(Time.times)
