# This file is placed in the Public Domain.


"logging tests"


import unittest


from nxt.defines import Main


class TestConfig(unittest.TestCase):

    def test_construct(self):
        config = Main()
        self.assertTrue(config)

    def test_main(self):
        Main.a = "b"
        self.assertEqual(Main.a, "b")

    def test_missing(self):
        self.assertFalse(Main.b)
