# This file is placed in the Public Domain.


"output"


import unittest


from nixt.clients import Output


class TestOutput(unittest.TestCase):

    "output unittests"

    def test_construct(self):
        "test output construction."
        output = Output()
        self.assertTrue(type(output), Output)
