# This file is placed in the Public Domain.


"utilities"


import time
import unittest


from nixt.defines import Utils


class TestUtils(unittest.TestCase):

    "utility unittests"

    def test_construct(self):
        "test utils construction."
        utils = Utils()
        self.assertTrue(type(utils), Utils)

    def test_strptime(self):
        "test extracting time."
        date = time.strptime("2019-3-4 22:22", "%Y-%m-%d %H:%M")
        self.assertTrue(date is not None)
