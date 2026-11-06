# This file is placed in the Public Domain.


"runners"


import unittest


from nixt.pooling import Runner


class TestRunner(unittest.TestCase):

    "runner unittests"

    def test_construct(self):
        "test runner construction."
        runner = Runner()
        self.assertTrue(type(runner), Runner)
