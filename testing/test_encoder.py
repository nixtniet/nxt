# This file is placed in the Public Domain.
# type: ignore


"encoder/decoder"


import unittest


from nixt.defines import Object, JSON, Method


VALIDJSON = '{"test": "bla"}'


class TestEncoder(unittest.TestCase):

    "encoder unittests"

    def test_dumps(self):
        "test dump string."
        obj = Object()
        obj.test = "bla"
        self.assertEqual(JSON.dumps(obj), VALIDJSON)


class TestDecoder(unittest.TestCase):

    "decoder unittests"

    def test_loads(self):
        "test load string."
        obj = Object()
        obj.test = "bla"
        oobj = Object()
        Method.construct(oobj, JSON.loads(JSON.dumps(obj)))
        self.assertEqual(getattr(oobj, "test", None), "bla")


class TestTypes(unittest.TestCase):

    "types unittests"

    def test_dict(self):
        "test dumps/loads dictionary."
        obj = JSON.loads(JSON.dumps({"a": "b"}))
        self.assertEqual(obj, {"a": "b"})

    def test_integer(self):
        "test dumps/loads an integer."
        obj = JSON.loads(JSON.dumps(1))
        self.assertEqual(obj, 1)

    def test_float(self):
        "test dumps/loads floating point."
        obj = JSON.loads(JSON.dumps(1.0))
        self.assertEqual(obj, 1.0)

    def test_string(self):
        "test dumps/loads a string."
        obj = JSON.loads(JSON.dumps("test"))
        self.assertEqual(obj, "test")

    def test_true(self):
        "test dumps/loads boolean true."
        obj = JSON.loads(JSON.dumps(True))
        self.assertEqual(obj, True)

    def test_false(self):
        "test dumps/loads boolean false."
        obj = JSON.loads(JSON.dumps(False))
        self.assertEqual(obj, False)

    def test_object(self):
        "test object containment."
        ooo = Object()
        ooo.a = "b"
        obj = Object()
        Method.update(obj, JSON.loads(JSON.dumps(ooo)))
        self.assertTrue(getattr(obj, "a", False))
