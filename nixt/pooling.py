# This file is placed in the Public Domain.


"runners/clients"


import os


from .looping import Loop
from .utility import RLock


class Runner(Loop):

    "run jobs"

    def run(self, *args, **kwargs):
        "fetch a feed."
        raise NotImplementedError

    def loop(self):
        "loop to handle fetch jobs."
        while not self.stopped.is_set():
            job = self.queue.get()
            if job is None:
                break
            self.run(*job)
        self.done.set()

    def wait(self):
        "skip wait."


class Pool:

    "multiple runners"

    runners = []
    clazz = Runner
    lock = RLock()
    max = os.cpu_count()
    nrcpu = 1
    nrlast = 0

    @classmethod
    def add(cls, runner):
        "add a runner."
        cls.runners.append(runner)

    @classmethod
    def busy(cls):
        "see if pool is busy."
        return any(runner.queue.qsize() for runner in cls.runners)

    @classmethod
    def init(cls, nrs, clz=None):
        "initialze a number of runners."
        cls.nrcpu = nrs
        if clz:
            cls.clazz = clz
        for nr in range(nrs):
            runner = cls.clazz()
            runner.start(name=f"Runner{nr}")
            cls.add(runner)

    @classmethod
    def put(cls, *args):
        "push job to a runner."
        with cls.lock:
            if cls.nrlast-1 >= len(cls.runners)-1:
                cls.nrlast = 0
            clt = cls.runners[cls.nrlast-1]
            clt.put(*args)
            cls.nrlast += 1


def __dir__():
    return (
        'Pool',
        'Runner'
    )
