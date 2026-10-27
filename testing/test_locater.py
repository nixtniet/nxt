# This file is placed in the Public Domain.


"logging tests"


import unittest


from nixt.defines import Locater


class TestLocater(unittest.TestCase):

    "locater unittests"

    def test_construct(self):
        "test locater construction."
        locater = Locater()
        self.assertTrue(locater)
