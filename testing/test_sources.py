# This file is placed in the Public Domain.


"md5sums"


import unittest


from nixt.defines import MD5


class TestMD5(unittest.TestCase):

    "MD% unittests"

    def test_construct(self):
        "test MD5 construction."
        md5 = MD5()
        self.assertTrue(type(md5), MD5)
