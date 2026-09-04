# This file is placed in the Public Domain.


"module management"


import unittest


from nxt.defines import Mods


class TestPackage(unittest.TestCase):

    def test_dir(self):
        Mods.dir("mods", "mods")
        self.assertTrue("mods" in Mods.dirs)
