# This file is placed in the Public Domain.


"message handler"


from .looping import Loop
from .tasking import Task


class Handler(Loop):

    "run callbacks"

    def __init__(self):
        super().__init__()
        self.cbs = {}

    def handle(self, msg):
        "run callback function with msg."
        func = self.cbs.get(msg.kind, None)
        if not func:
            msg.ready()
            return
        name = msg.text and msg.text.split()[0]
        msg._thr = Task.start(func, msg, name=name)

    def register(self, kind, callback):
        "register callback."
        self.cbs[kind] = callback


def __dir__():
    return (
        'Handler',
    )
