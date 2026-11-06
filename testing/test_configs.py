# This file is placed in the Public Domain.
# type: ignore


"logging tests"


import unittest


from nixt.defines import Config, Main


class TestConfig(unittest.TestCase):

    "configuration unittest"

    def test_construct(self):
        "test constructing config."
        config = Config("test", (), {})
        self.assertTrue(type(config), Config)


class TestMain(unittest.TestCase):

    "test main configuration"

    def test_construct(self):
        "test config construction."
        main = Main()
        self.assertTrue(type(main), Main)

    def test_main(self):
        "test main config."
        Main.a = "b"
        self.assertEqual(Main.a, "b")

    def test_missing(self):
        "test missing attribute."
        self.assertFalse(Main.b)
