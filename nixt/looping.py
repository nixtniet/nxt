# This file is placed in the Public Domain.


"the big loop"


import _thread


from .tasking import Task
from .utility import Event, Queue


class Loop:

    "keep looping"

    def __init__(self):
        self.queue = Queue()
        self.stopped = Event()
        self.done = Event()

    def after(self, msg):
        "called after callback."

    def handle(self, msg):
        "handle msg."

    def loop(self):
        "callback loop."
        while not self.stopped.is_set():
            self.poll()
            msg = self.queue.get()
            if msg is None:
                self.queue.task_done()
                break
            msg.orig = repr(self)
            self.handle(msg)
            self.after(msg)
            self.queue.task_done()
        self.done.set()

    def poll(self):
        "create msg and put it on the queue."

    def put(self, msg):
        "put msg on queue."
        self.queue.put(msg)

    def start(self, daemon=True, name=None):
        "start callback loop."
        self.done.clear()
        self.stopped.clear()
        Task.start(self.loop, daemon=daemon, name=name)

    def stop(self):
        "stop xallback loop."
        self.stopped.set()
        self.queue.put(None)
        self.done.wait()

    def wait(self):
        "wait for all msgs to finish,"
        try:
            self.queue.join()
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


def __dir__():
    return (
        'Loop'
    )
