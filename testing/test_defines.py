# This file is placed in the Public Domain.


"definitions"


import unittest


import nixt.defines as dev


class TestDefines(unittest.TestCase):

    "defines unittest"

    def test_dir(self):
        "internal interface check."
        self.assertEqual(len(dir(dev)), 39)
