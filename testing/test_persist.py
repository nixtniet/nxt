# This file is placed in the Public Domain.
# type: ignore


"persist tests"


import os
import unittest


from nixt.defines import Disk, Main, Locater, Method, Workdir
from nixt.persist import Cache


Workdir.wdr = '.test'


class TestCache(unittest.TestCase):

    "cache unittests"

    def test_construct(self):
        "test cache construction."
        cache = Cache()
        self.assertTrue(type(cache), Cache)


class TestDisk(unittest.TestCase):

    "disk unittests"

    def test_construct(self):
        "test disl construction."
        disk = Disk()
        self.assertTrue(type(disk), Disk)

    def test_loadcfg(self):
        "test loading from disk."
        Main.a = "b"
        Disk.read(Main, "main", "config")
        self.assertEqual(getattr(Main, "a", None), "b")

    def test_save(self):
        "test saving to disk."
        obj = Method()
        opath = Disk.write(obj)
        self.assertTrue(os.path.exists(os.path.join(Workdir.wdr, "store", opath)))

    def test_writecfg(self):
        "test writing config to disk."
        Main.a = "b"
        Disk.write(Main, "main", "config")
        self.assertTrue(os.path.exists(os.path.join(Workdir.wdr, "config", "main")))


class TestLocater(unittest.TestCase):

    "locater unittests"

    def test_construct(self):
        "test locater construction."
        locater = Locater()
        self.assertTrue(type(locater), Locater)


class TestWorkdir(unittest.TestCase):

    "workdir unittests"

    def test_construct(self):
        "test workdir construction."
        workdir = Workdir()
        self.assertTrue(type(workdir), Workdir)
