# This file is placed in the Public Domain.


"watching files"


import os
import time


from .default import Event
from .tasking import Task


class Watcher:

    "watch files"

    cbs = {}
    sleep  = 1.0
    stopped = Event()
    times = {}

    @classmethod
    def add(cls, path, callback):
        "add callback."
        if not os.path.exists(path):
            return
        cls.cbs[path] = callback

    @classmethod
    def init(cls, times=None):
        "read timestamps."
        if times is None:
            times= {}
        for path in cls.cbs:
            if not os.path.exists(path):
                continue
            cls.times[path] = times.get(path, os.stat(path).st_mtime)

    @classmethod
    def loop(cls):
        "loop select."
        while not cls.stopped.is_set():
            for path, callback in cls.cbs.items():
                if not os.path.exists(path):
                    continue
                mtime = os.stat(path).st_mtime
                if mtime > cls.times[path]:
                    callback()
                cls.times[path] = mtime
            time.sleep(cls.sleep)

    @classmethod
    def start(cls, daemon=True):
        "start callback loop."
        if not cls.stopped.is_set():
            return
        Task.start(cls.loop, daemon=daemon)

    @classmethod
    def stop(cls):
        "stop xallback loop."
        cls.stopped.set()


def __dir__():
    return (
        'Watcher',
    )
