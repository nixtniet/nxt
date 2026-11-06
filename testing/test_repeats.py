# This file is placed in the Public Domain.


"repeater"


import unittest


from nixt.repeats import Repeater


class TestRepeater(unittest.TestCase):

    "repeater unittests"

    def test_construct(self):
        "test repeater construction."
        repeater = Repeater()
        self.assertTrue(type(repeater), Repeater)
