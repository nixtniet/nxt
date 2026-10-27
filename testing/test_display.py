# This file is placed in the Public Domain.


"display"


import unittest


from nixt.clients import Display


class TestDisplay(unittest.TestCase):

    "display unittest"

    def test_construct(self):
        "test display contruction."
        display = Display()
        self.assertTrue(type(display), Display)
