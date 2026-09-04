# This file is placed in the Public Domain.


"logging tests"


import unittest


from nxt.defines import Object, Method


class TestMethod(unittest.TestCase):

    def test_clear(self):
        obj = Object()
        obj.a = "b"
        Method.clear(obj)
        self.assertEqual(str(obj), "{}")
