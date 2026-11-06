# This file is placed in the Public Domain.


"display"


import unittest


from nixt.defines import Screen


class TestScreen(unittest.TestCase):

    "screen unittest"

    def test_construct(self):
        "test screen construction."
        screen = Screen()
        self.assertTrue(type(screen), Screen)
