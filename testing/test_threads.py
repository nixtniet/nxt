# This file is placed in the Public Domain.


"threads"


import unittest


from nixt.tasking import Task


buffer = []


def test():
    "append to buffer."
    buffer.append("test")


class TestThreading(unittest.TestCase):

    "thread unittests"

    def test_construct(self):
        "test thread construction."
        task = Task()
        self.assertTrue(type(task), Task)
