# This file is placed in the Public Domain.


"non-blocking"


import inspect
import logging
import time
import _thread


from .default import Event, Queue, RLock, Thread
from .excepts import Errors


logger = logging.getLogger(__name__)


class Worker(Thread):

    "unit of thread"

    block = Event()

    def __init__(self, func, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, None, (), daemon=daemon)
        self.name = kwargs.get("name", self.getname(func) or "")
        self.queue = Queue()
        self.resul = None
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
            Errors.defer(ex)

    @classmethod
    def clsname(cls, obj):
        "class name of an object."
        if "__self__" in dir(obj):
            return obj.__self__.__class__.__name__
        return obj.__class__.__name__

    @classmethod
    def getname(cls, obj):
        "string of function/method."
        if inspect.ismethod(obj):
            return f"{cls.clsname(obj)}.{obj.__name__}"
        if inspect.isfunction(obj):
            return repr(obj).split()[1]
        return repr(obj)

    def run(self):
        "run function."
        func, args = self.queue.get()
        if self.block.is_set():
            return
        try:
            self.result = func(*args)
        except Exception as ex:
            Errors.defer(ex, *args)


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
