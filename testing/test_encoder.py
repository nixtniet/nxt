# This file is placed in the Public Domain.


"encoder/decoder"


import unittest


from nxt.defines import Object, JSON, Method


VALIDJSON = '{"test": "bla"}'


class TestEncoder(unittest.TestCase):

    def test_dumps(self):
        obj = Object()
        obj.test = "bla"
        self.assertEqual(JSON.dumps(obj), VALIDJSON)


class TestDecoder(unittest.TestCase):

    def test_loads(self):
        obj = Object()
        obj.test = "bla"
        oobj = JSON.loads(JSON.dumps(obj))
        self.assertEqual(oobj["test"], "bla")


class TestTypes(unittest.TestCase):

    def test_dict(self):
        obj = JSON.loads(JSON.dumps({"a": "b"}))
        self.assertEqual(obj, {"a": "b"})

    def test_integer(self):
        obj = JSON.loads(JSON.dumps(1))
        self.assertEqual(obj, 1)

    def test_float(self):
        obj = JSON.loads(JSON.dumps(1.0))
        self.assertEqual(obj, 1.0)

    def test_string(self):
        obj = JSON.loads(JSON.dumps("test"))
        self.assertEqual(obj, "test")

    def test_true(self):
        obj = JSON.loads(JSON.dumps(True))
        self.assertEqual(obj, True)

    def test_false(self):
        obj = JSON.loads(JSON.dumps(False))
        self.assertEqual(obj, False)

    def test_object(self):
        ooo = Object()
        ooo.a = "b"
        obj = Object()
        Method.update(obj, JSON.loads(JSON.dumps(ooo)))
        self.assertEqual(obj.a, "b")
