# This file is placed in the Public Domain.


"if it repeats it is important"


import time


from .default import Event
from .tasking import Task


class Repeater:

    "repeat at interval"

    running = Event()
    stopped = Event()
    counter = 0
    sleeptime = 0.1
    todo = {}

    @classmethod
    def add(
        cls,
        sleeptime,
        func,
        *args,
        **kwargs
        ):
        "add a repeater."
        slp = str(sleeptime)
        if slp not in cls.todo:
            cls.todo[slp] = []
        cls.todo[slp].append((func, args, kwargs))

    @classmethod
    def loop(cls):
        "repeater loop."
        while not cls.stopped.is_set():
            time.sleep(1.0)
            cls.counter += 1
            for sleeptime, arguments in cls.todo.items():
                slept = int(sleeptime)
                if cls.counter % slept != 0:
                    continue
                for func, args, kwargs in arguments:
                    Task.start(func, *args, **kwargs)

    @classmethod
    def start(cls, daemon=True):
        "start callback loop."
        if not cls.stopped.is_set():
            Task.start(cls.loop, daemon=daemon, name="Repeater.loop")

    @classmethod
    def stop(cls):
        "stop loop."
        cls.stopped.set()

    @classmethod
    def wait(cls):
        "wait for loop to stop."


def __dir__():
    return (
        'Repeater',
    )
