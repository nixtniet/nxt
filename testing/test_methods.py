# This file is placed in the Public Domain.
# type: ignore
# pylint: disable=W0201


"logging tests"


import unittest


from nixt.defines import Object, Method


class Mine(Object):

    "custom object"


class TestMethod(unittest.TestCase):

    "method unittests"

    def test_construct(self):
        "test method construction."
        method = Method()
        self.assertTrue(type(method), Method)

    def test_clear(self):
        "test clearing an object."
        obj = Mine()
        obj.a = "b"
        Method.clear(obj)
        self.assertEqual(str(obj), "{}")

    def test_class(self):
        "test calling __class__ on an object."
        obj = Mine()
        clz = obj.__class__()
        self.assertTrue("Mine" in str(type(clz)))

    def test_contains(self):
        "test containment of a key."
        obj = Mine()
        obj.key = "value"
        self.assertTrue("key" in obj)

    def test_delattr(self):
        "test deleting an attribute."
        obj = Mine()
        obj.key = "value"
        del obj.key
        self.assertTrue("key" not in obj)

    def test_dict(self):
        "test for __dict__."
        obj = Mine()
        self.assertEqual(obj.__dict__, {})

    def test_format(self):
        "test formatting an object."
        obj = Mine()
        self.assertEqual(format(obj, ""), "{}")

    def test_getattribute(self):
        "test getting an attribute/"
        obj = Mine()
        obj.key = "value"
        self.assertEqual(getattr(obj, "key", None), "value")

    def test_hash__(self):
        "test hasing an object."
        obj = Mine()
        hsj = hash(obj)
        self.assertTrue(isinstance(hsj, int))

    def test_init(self):
        "test object construction."
        obj = Mine()
        self.assertTrue(type(obj), Mine)

    def test_iter(self):
        "test iterating over an object."
        obj = Mine()
        obj.key = "value"
        self.assertTrue(list(iter(obj)), ["key",])

    def test_format2(self):
        "test formatting an object."
        o = Mine()
        o.a = "b"
        self.assertEqual(Method.fmt(o), 'a="b"')

    def test_getattr(self):
        "test attribute access."
        obj = Mine()
        obj.key = "value"
        self.assertEqual(obj.key, "value")

    def test_keys(self):
        "test listing keys of an object."
        obj = Mine()
        obj.key = "value"
        self.assertEqual(list(Method.keys(obj)), ["key"])

    def test_len(self):
        "testing length of an object."
        obj = Mine()
        self.assertEqual(len(obj), 0)

    def test_items(self):
        "check items of an object."
        obj = Mine()
        obj.key = "value"
        self.assertEqual(list(Method.items(obj)), [("key", "value")])

    def test_repr(self):
        "test repr() on an object."
        self.assertTrue(
                        repr(Method.update(Object(), {"key": "value"})),
                        {"key": "value"}
                       )

    def test_setattr(self):
        "test setting an attribute."
        obj = Mine()
        obj.key = "value"
        self.assertTrue(obj.key, "value")

    def test_str(self):
        "test concerting an object to a string."
        obj = Mine()
        self.assertEqual(str(obj), "{}")

    def test_update(self):
        "test updating an object."
        obj = Mine()
        obj.key = "value"
        oobj = Mine()
        Method.update(oobj, obj)
        self.assertTrue(oobj.key, "value")

    def test_values(self):
        "test fetching values of an object."
        obj = Mine()
        obj.key = "value"
        self.assertEqual(list(Method.values(obj)), ["value"])
