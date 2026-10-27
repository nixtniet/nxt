# This file is placed in the Public Domain.


"obejcts tests"


import unittest


from nixt.defines import Data, Object


class Mine(Object):

    "custom object"

    def __init__(self):
        Object.__init__(self)
        self.a = ""
        self.obj = Object()


class TestData(unittest.TestCase):

    "data unittests"

    def construct(self):
        "test data construction."
        data = Data()
        self.assertTrue(type(data), Data)


class TestObject(unittest.TestCase):

    "object unittests"

    def construct(self):
        "test object construction."
        obj = Object()
        self.assertTrue(type(obj), Object)


class TestComposite(unittest.TestCase):

    "composition unittests"

    def testcomposite(self):
        "test composition."
        obj = Mine()
        obj.obj = Mine()
        obj.obj.a = "test"
        self.assertEqual(obj.obj.a, "test")
