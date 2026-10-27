# This file is placed in the Public Domain.


"time related"


import unittest


from nixt.defines import Time


class TestTime(unittest.TestCase):

    "time unittests"

    def construct(self):
        "test time construction."
        time = Time()
        self.assertTrue(type(time), Time)

    def test_times(self):
        "test times definitions."
        self.assertTrue(Time.times)
