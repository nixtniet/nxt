# This file is placed in the Public Domain.


"pool"


import unittest


from nixt.pooling import Pool


class TestPool(unittest.TestCase):

    "pool unittests"

    def test_construct(self):
        "test pool construction."
        pool = Pool()
        self.assertTrue(type(pool), Pool)
