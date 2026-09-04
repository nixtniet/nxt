# This file is placed in the Public Domain.


"logging tests"


import unittest


from nxt.defines import Object, Parser


class TestParse(unittest.TestCase):

    def test_parse(self):
        obj = Object()
        obj.cmd = ""
        Parser.parse(obj, "cmd")
        print(obj)
        self.assertEqual(obj.cmd, "cmd")
