# This file is placed in the Public Domain.


"definitions"


import unittest


import nxt.defines as dev


class TestDefines(unittest.TestCase):

    def test_dir(self):
        self.assertTrue(len(dir(dev)), 22)
