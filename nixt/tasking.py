# This file is placed in the Public Domain.


"non-blocking"


import inspect


from .default import Event, Log, RLock, Thread


logger = Log(__name__)


class Task:

    "start a task"

    block = Event()
    lock = RLock()

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

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

    @classmethod
    def start(cls, func, *args, daemon=True, **kwargs):
        "start a new thread running function with arguments."
        with cls.lock:
            if cls.block.is_set():
                return
            name = kwargs.get("name", None)
            if name:
                del kwargs["name"]
            else:
                name = cls.getname(func)
            worker = Thread(None, func, name, args, kwargs, daemon=daemon)
            worker.start()
            return worker


def __dir__():
    return (
        'Task',
    )
