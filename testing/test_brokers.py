# This file is placed in the Public Domain.


"an object for a string"


import unittest


from nixt.defines import Broker, Object


class TestBroker(unittest.TestCase):

    "brokers unittest"

    broker = Broker()

    def test_construct(self):
        "test broker construction."
        broker = Broker()
        self.assertTrue(broker.objects)

    def test_add(self):
        "add an object to the broker."
        obj = Object()
        self.broker.add(obj)
        self.assertTrue(obj in self.broker.objects.values())

    def test_get(self):
        "test object fetching from broker."
        obj = Object()
        self.broker.add(obj)
        obj2 = self.broker.get(repr(obj))
        self.assertEqual(obj, obj2)

    def test_has(self):
        "check whether broker has an object."
        obj = Object()
        self.broker.add(obj)
        self.assertTrue(self.broker.has(obj))

    def test_like(self):
        "test whether look-a-lke gets found."
        obj = Object()
        self.broker.add(obj)
        self.assertTrue(repr(obj) in [x[0] for x in self.broker.like("object")])

    def test_remove(self):
        "testing removing an object."
        obj = Object()
        self.broker.add(obj)
        self.broker.remove(obj)
        self.assertTrue(obj not in self.broker.objects.values())
