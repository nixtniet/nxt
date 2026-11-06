# This file is placed in the Public Domain.


"logging"


import unittest


from nixt.defines import Format, Logging


class TestFormat(unittest.TestCase):

    "format unittests"

    def test_construct(self):
        "test format construction."
        fmt = Format()
        self.assertTrue(type(fmt), Format)


class TestLogging(unittest.TestCase):

    "logging unittests"

    def test_construct(self):
        "test logging construction."
        logger = Logging()
        self.assertTrue(type(logger), Logging)
