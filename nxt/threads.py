# This file is placed in the Public Domain.


"non-blocking"


import inspect
import logging
import os
import queue
import threading
import time
import _thread


b = os.path.basename
e = os.path.exists


class Engine:

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.done = threading.Event()

    def after(self, event):
        "called after callback."

    def callback(self, event):
        "run callback function with event."
        func = self.cbs.get(event.kind, None)
        if not func:
            event.ready()
            return
        name = event.text and event.text.split()[0]
        event._thr = Thread.launch(func, event, name=name)

    def loop(self):
        "callback loop."
        while not self.stopped.is_set():
            self.poll()
            event = self.queue.get()
            if event is None:
                self.queue.task_done()
                break
            event.orig = repr(self)
            self.callback(event)
            self.after(event)
            self.queue.task_done()
        self.done.set()

    def poll(self):
        "create event and put it on the queue."

    def put(self, event):
        "put event on queue."
        self.queue.put(event)

    def register(self, kind, callback):
        "register callback."
        self.cbs[kind] = callback

    def start(self, daemon=True):
        "start callback loop."
        self.done.clear()
        self.stopped.clear()
        Thread.launch(self.loop, daemon=daemon)

    def stop(self):
        "stop xallback loop."
        self.stopped.set()
        self.queue.put(None)
        self.done.wait()

    def wait(self):
        "wait for all events to finish,"
        try:
            self.queue.join()
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


class Output:

    def __init__(self):
        self.oqueue = queue.Queue()
        self.ostopped = threading.Event()

    def display(self, event):
        "do actual display."

    def output(self):
        "output loop."
        while not self.ostopped.is_set():
            try:
                event = self.oqueue.get()
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()
            if event is None:
                self.oqueue.task_done()
                break
            self.display(event)
            self.oqueue.task_done()

    def raw(self, text):
        "raw output."
        raise NotImplementedError

    def start(self, daemon=True):
        "start output loop."
        self.ostopped.clear()
        Thread.launch(self.output, daemon=daemon)

    def stop(self):
        "stop output loop."
        self.ostopped.set()
        self.oqueue.put(None)

    def wait(self):
        "wait for output to finish."
        try:
            self.oqueue.join()
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()


class Task(threading.Thread):

    block = threading.Event()

    def __init__(self, func, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, None, (), daemon=daemon)
        self.event = None
        self.name = kwargs.get("name", Thread.name(func))
        self.queue = queue.Queue()
        self.result = None
        self.starttime = time.time()
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

    def join(self, timeout=0.0):
        "join thread and return result."
        try:
            super().join(timeout or None)
            return self.result
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()

    def run(self):
        "run function."
        func, args = self.queue.get()
        if self.block.is_set():
            return
        try:
            self.result = func(*args)
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()


class Thread:

    lock = threading.RLock()

    @classmethod
    def launch(cls, func, *args, **kwargs):
        "start a new thread running function with arguments."
        with cls.lock:
            "run function in a thread."
            task = Task(func, *args, **kwargs)
            task.start()
            return task

    @classmethod
    def clsname(cls, obj):
        "class name of an object."
        if "__self__" in dir(obj):
            return obj.__self__.__class__.__name__
        return obj.__class__.__name_

    @classmethod
    def name(cls, obj):
        "string of function/method."
        if inspect.ismethod(obj):
            return f"{cls.clsname(obj)}.{obj.__name__}"
        if inspect.isfunction(obj):
            return repr(obj).split()[1]
        return repr(obj)


class Watcher:

    running = threading.Event()
    sleep = 1.0
    cbs = {}
    times = {}

    @classmethod
    def add(cls, path, callback):
        "add callback"
        if not os.path.exists(path):
            return
        cls.cbs[path] = callback
        
    @classmethod
    def callback(cls, path):
        "run callback."
        cls.cbs[path]()

    @classmethod
    def init(cls, times={}):
        "read timestamps."
        for path in cls.cbs:
            if not e(path):
                continue
            cls.times[path] = times.get(path, os.stat(path).st_mtime)
            
    @classmethod
    def loop(cls):
        "loop select."
        while cls.running.isSet():
            for path in cls.cbs:
                if not e(path):
                    continue
                mtime = os.stat(path).st_mtime
                if mtime > cls.times[path]:
                    cls.callback(path)
                cls.times[path] = mtime
            time.sleep(cls.sleep)

    @classmethod
    def start(cls, times={}):
        "start watcher"
        if cls.running.isSet():
            return
        cls.running.set()
        cls.init(times)
        Thread.launch(cls.loop, name="Watcher.loop")

    @classmethod
    def stop(cls):
        "stop watcher."
        cls.running.clear()

def __dir__():
    return (
        'Engine',
        'Output',
        'Task',
        'Thread',
        'Watcher'
    )
