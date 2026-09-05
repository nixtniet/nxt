# This file is placed in the Public Domain.


"runners"


import os
import queue
import threading


from .threads import Thread


class Runner:

    def __init__(self):
        self.queue = queue.Queue()
        self.running = threading.Event()

    def run(self, *args, **kwargs):
        "fetch a feed."
        raise NotImplementedError

    def loop(self):
        "loop to handle fetch jobs."
        while self.running.is_set():
            job = self.queue.get()
            if job is None:
                break
            self.run(*job)

    def put(self, *args):
        "put jobs on queue."
        self.queue.put(args)

    def start(self, daemon=True):
        "start runner."
        self.running.set()
        Thread.launch(self.loop, daemon=daemon)

    def stop(self):
        "stop runner."
        self.running.clear()
        self.queue.put(None)


class Runners:

    def __init__(self, clazz=None):
        self.clazz = clazz or Runner()
        self.runners = []
        self.max = os.cpu_count()
        self.nrcpu = 1
        self.nrlast = 0

    def add(self, client):
        "add a runner."
        self.runners.append(client)

    def busy(self):
        for runner in self.runners:
            if runner.queue.qsize():
                return True
        return False

    def init(self, nr):
        "initialze a number of runners."
        for x in range(nr):
            runner = self.clazz()
            runner.start()
            self.add(runner)

    def put(self, *args):
        "push job to a runner."
        if not self.runners:
            self.init(1)
        if self.nrlast > self.nrcpu-1:
            self.nrlast = 0
        clt = self.runners[self.nrlast]
        clt.put(*args)
        self.nrlast += 1


def __dir__():
    return (
        'Runner',
        'Runners'
    )
