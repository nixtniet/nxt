# This file is placed in the Public Domain.


"static tables"


import unittest


from nixt.statics import CORE


class TestStatics(unittest.TestCase):

    "statics unittests"

    def test_core(self):
        "test for core definitions."
        self.assertTrue(CORE)
