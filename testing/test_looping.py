# This file is placed in the Public Domain.


"looping"


import unittest


from nixt.looping import Loop


class TestLoop(unittest.TestCase):

    "looping unittests"

    def test_construct(self):
        "test loop construction."
        loop = Loop()
        self.assertTrue(type(loop), Loop)
