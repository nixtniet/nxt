# This file is placed in the Public Domain.


"logging tests"


import unittest


from nixt.defines import Object, Parser


class Mine(Object):

    "custom object."

    def __init__(self):
        Object.__init__(self)
        self.cmd = ""


class TestParse(unittest.TestCase):

    "parsing unittests"

    def test_parse(self):
        "test command parsing."
        obj = Mine()
        Parser.parse(obj, "cmd")
        self.assertEqual(obj.cmd, "cmd")
