# This file is placed in the Public Domain.


"in the beginning"


import unittest


from nixt.defines import Boot, Task


class TestRuntime(unittest.TestCase):

    "runtime unittests"

    def setUp(self):
        "setup boot object."
        self.boot = Boot()

    def shutDown(self):
        "boot shutdown."
        self.boot.shutdown()

    def test_construct(self):
        "test boot construcion."
        self.assertEqual(type(self.boot), Boot)

    def test_configure(self):
        "test configuration."
        self.assertEqual(self.boot.configure(), None)

    def test_forever(self):
        "test main loop."
        task = Task.start(self.boot.forever)
        self.boot.running.clear()
        task.join()
        self.assertEqual(self.boot.stopped.is_set(), True)

    def test_init(self):
        "test initialising modules."
        self.assertEqual(self.boot.init(""), True)

    def test_shutdown(self):
        "test shutdown/"
        task = Task.start(self.boot.shutdown, False)
        task.join()
        self.assertTrue(self.boot.stopped.is_set())

    def test_wrapped(self):
        "test wrapping main function."
        self.assertFalse(self.boot.wrapped(print, "hello world"))
