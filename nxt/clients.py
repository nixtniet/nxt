# This file is placed in the Public Domain.


"clients"


import gc
import logging
import queue
import threading
import _thread
import time


from .threads import Engine, Output


class Broker:

    objects = {}

    @classmethod
    def add(cls, obj):
        "add object to the broker, key is repr(obj)."
        id = repr(obj)
        cls.objects[id] = obj
        return id

    @classmethod
    def get(cls, origin):
        "object by repr(obj)."
        return cls.objects.get(origin)

    @classmethod
    def has(cls, obj):
        "whether the Broker has object."
        return repr(obj) in cls.objects

    @classmethod
    def like(cls, txt):
        "all keys with a substring in their key."
        for orig in cls.objects:
            if txt in orig.split()[0]:
                yield orig, cls.get(orig)

    @classmethod
    def objs(cls, attr):
        "objects with a certain attribute."
        for obj in cls.objects.values():
            if attr in dir(obj):
                yield obj


class Display:

    block = threading.Event()

    def __init__(self):
        super().__init__()
        self.olock = threading.RLock()
        self.silent = False
        Broker.add(self)

    def announce(self, text):
        "announce text to all channels."
        if not self.silent:
            self.raw(text)

    def display(self, event):
        "display event results."
        with self.olock:
            for txt in event.result:
                if self.block.is_set():
                    return
                self.dosay(event.channel, txt)
        del event
        gc.collect()

    def dosay(self, channel, text):
        "say called by display."
        self.say(channel, text)

    def raw(self, text):
        "raw output."
        raise NotImplementedError

    def say(self, channel, text):
        "say text in channel."
        self.raw(text)


class Client(Engine, Display):

    def __init__(self):
        Engine.__init__(self)
        Display.__init__(self)

    def raw(self, text):
        "raw output."
        raise NotImplementedError


class Buffered(Client, Output):

    def __init__(self):
        Client.__init__(self)
        Output.__init__(self)

    def raw(self, text):
        "raw output."
        raise NotImplementedError

    def start(self, daemon=True):
        "start output loop."
        Client.start(self)
        Output.start(self, daemon=daemon)

    def stop(self):
        "stop output loop."
        Client.stop(self)
        Output.stop(self)


class Clients:

    @staticmethod
    def announce(txt):
        "announce text on all clients."
        for obj in Broker.objs("announce"):
            obj.announce(txt)

    @staticmethod
    def display(evt):
        "display results."
        bot = Broker.get(evt.orig)
        if bot:
            bot.display(evt)

    @staticmethod
    def shutdown():
        "call stop on clients."
        for client in Broker.objs("wait"):
            try:
                client.wait()
            except (KeyboardInterrupt, EOFError):
                pass
        time.sleep(0.01)
        for client in Broker.objs("stop"):
            try:
                client.stop()
            except (KeyboardInterrupt, EOFError):
                pass
        time.sleep(0.01)


def __dir__():
    return (
        'Broker',
        'Client',
        'Clients',
        'Buffered',
        'Display'
    )
