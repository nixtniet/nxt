# This file is placed in the Public Domain.


"watcher"


import unittest


from nixt.watcher import Watcher


class TestWatcher(unittest.TestCase):

    "watcher unittests"

    def test_construct(self):
        "test watcher construction."
        watcher = Watcher()
        self.assertTrue(type(watcher), Watcher)
