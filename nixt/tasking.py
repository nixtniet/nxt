# This file is placed in the Public Domain.


"non-blocking"


import time


from .excepts import Errors
from .methods import Method
from .utility import Event, Log, Queue, RLock, Thread


logger = Log(__name__)


class Worker(Thread):

    "unit of thread"

    block = Event()

    def __init__(self, func, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, None, (), daemon=daemon)
        self.name = kwargs.get("name", "")
        if not self.name:
            self.name = Method.getname(func) or ""
        self.queue = Queue()
        self.result = None
        self.sleep = 0.0
        self.starttime = time.time()
        self.state = {}
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

    def join(self, timeout=None):
        "join thread and return result."
        try:
            super().join(timeout or None)
            return self.result
        except Exception as ex:
            Worker.block.set()
            Errors.throw(ex)

    def run(self):
        "run function."
        func, args = self.queue.get()
        if self.block.is_set():
            return
        try:
            self.result = func(*args)
        except Exception as ex:
            Worker.block.set()
            Errors.throw(ex, *args)


class Task:

    "start a task"

    lock = RLock()

    @classmethod
    def start(cls, func, *args, **kwargs):
        "start a new thread running function with arguments."
        with cls.lock:
            worker = Worker(func, *args, **kwargs)
            worker.start()
            return worker


def __dir__():
    return (
        'Task',
        'Worker'
    )
