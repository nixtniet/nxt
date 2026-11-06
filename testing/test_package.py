# This file is placed in the Public Domain.


"module management"


import unittest


from nixt.defines import Mods


class TestMods(unittest.TestCase):

    "modules unittest"

    def test_construct(self):
        "test mods construction."
        mods = Mods()
        self.assertTrue(type(mods), Mods)

    def test_dir(self):
        "test setting modules directory."
        Mods.dir("mods", "mods")
        self.assertTrue("mods" in Mods.dirs)
