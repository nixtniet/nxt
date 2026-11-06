# This file is placed in the Public Domain.


"buffers"


import unittest


from nixt.clients import Buffer


class TestBuffer(unittest.TestCase):

    "buffer unittests"

    def test_construct(self):
        "test biffer construction."
        buffer = Buffer()
        self.assertTrue(type(buffer), Buffer)
