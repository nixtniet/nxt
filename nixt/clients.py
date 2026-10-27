# This file is placed in the Public Domain.


"displaying messages"


import _thread


from .default import Event, RLock, Queue
from .handler import Handler
from .tasking import Task


class Broker:

    "map repr(obj) to obj"

    objects = {}

    @classmethod
    def add(cls, obj):
        "add object to the broker, key is repr(obj)."
        cls.objects[repr(obj)] = obj

    @classmethod
    def get(cls, origin):
        "object by repr(obj)."
        return cls.objects.get(origin)

    @classmethod
    def has(cls, obj):
        "whether the Broker has object."
        return repr(obj) in cls.objects

    @classmethod
    def like(cls, text):
        "all keys with a substring in their key."
        for orig in cls.objects:
            if text in orig.split()[0]:
                yield (orig, cls.get(orig))

    @classmethod
    def objs(cls, attr):
        "objects with a certain attribute."
        for obj in cls.objects.values():
            if attr in dir(obj):
                yield obj

    @classmethod
    def remove(cls, obj):
        "remove object."
        del cls.objects[repr(obj)]


class Display:

    "unit of display"

    block = Event()
    last = ""

    def __init__(self):
        self.olock = RLock()
        self.silent = False
        Broker.add(self)

    def announce(self, text):
        "announce text to all channels."
        if not self.silent:
            self.raw(text)

    def display(self, msg):
        "display msg results."
        with self.olock:
            for txt in msg.result:
                if self.block.is_set():
                    return
                self.dosay(msg.channel, txt)
                del txt
        del msg

    def dosay(self, channel, text):
        "say called by display."
        self.say(channel, text)

    def raw(self, text):
        "raw output."
        raise NotImplementedError

    def say(self, channel, text):
        "say text in channel."
        self.last = channel
        self.raw(text)


class Output(Display):

    "dedicated output loop"

    def __init__(self):
        Display.__init__(self)
        self.oqueue = Queue()
        self.ostopped = Event()

    def display(self, msg):
        "do actual display."

    def output(self):
        "output loop."
        while not self.ostopped.is_set():
            try:
                msg = self.oqueue.get()
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()
            if msg is None:
                self.oqueue.task_done()
                break
            self.display(msg)
            self.oqueue.task_done()

    def raw(self, text):
        "raw output."
        raise NotImplementedError

    def start(self, daemon=True):
        "start output loop."
        self.ostopped.clear()
        Task.start(self.output, daemon=daemon)

    def stop(self):
        "stop output loop."
        self.ostopped.set()
        self.oqueue.put(None)

    def wait(self):
        "wait for output to finish."
        try:
            self.oqueue.join()
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


class Screen(Handler, Display):

    "display with coupled handler"

    def __init__(self):
        Handler.__init__(self)
        Display.__init__(self)

    def raw(self, text):
        "raw output."
        raise NotImplementedError


class Buffer(Handler, Output):

    "buffered output"

    def __init__(self):
        Handler.__init__(self)
        Output.__init__(self)

    def raw(self, text):
        "raw output."
        raise NotImplementedError

    def start(self, daemon=True):
        "start output loop."
        Handler.start(self)
        Output.start(self, daemon=daemon)

    def stop(self):
        "stop output loop."
        Handler.stop(self)
        Output.stop(self)


class Clients:

    "collection of clients"

    @staticmethod
    def announce(text):
        "announce text on all clients."
        for obj in Broker.objs("announce"):
            obj.announce(text)

    @staticmethod
    def display(msg):
        "display results."
        bot = Broker.get(msg.orig)
        if bot:
            bot.display(msg)


def __dir__():
    return (
        'Buffer',
        'Broker',
        'Clients',
        'Display',
        'Pit[ut',
        'Screen'
    )
