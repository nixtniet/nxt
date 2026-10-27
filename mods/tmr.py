# This file is placed in the Public Domain.


"timers"


import random
import time


from nixt.default import Event, RLock
from nixt.defines import Broker, Disk, Locater, Log, Method, Object
from nixt.defines import Task, Time


logger = Log(__name__)
rand = random.Random()


def init():
    "intialize the timer module."
    TimerLoop.start()
    logger.info("%s timers" , len(TimerLoop.timers))


def shutdown():
    "shutdown timer module."
    TimerLoop.stop()


class Timers(Object):

    "timers holder"


class TimerLoop:

    "timer loop"

    dosave = False
    lock = RLock()
    path = ""
    running = Event()
    timers = {}

    @classmethod
    def add(cls, tme, orig, channel,  txt):
        "add a timer."
        with cls.lock:
            cls.timers[str(tme)] = (orig, channel, txt)

    @classmethod
    def delete(cls, tme):
        "delete a timer."
        with cls.lock:
            del cls.timers[str(tme)]

    @classmethod
    def loop(cls):
        "timer loop."
        while cls.running.is_set():
            time.sleep(1.0)
            timed = time.time()
            remove = []
            for tme, args in cls.timers.items():
                if float(tme) < timed:
                    Task.start(cls.run, args)
                    remove.append(tme)
            for tme in remove:
                cls.dosave = True
                cls.delete(tme)

    @classmethod
    def run(cls, args):
        "run a timer."
        orig, channel, txt = args
        for origin, bot in Broker.like(orig):
            if not origin or not bot:
                continue
            bot.say(channel, txt)

    @classmethod
    def start(cls):
        "start timers."
        cls.path = Locater.first(cls.timers) or "mods.tmr.Timer"
        cls.running.set()
        Task.start(cls.loop, name="Timers.loop")

    @classmethod
    def stop(cls):
        "stop timers."
        cls.running.clear()
        if cls.timers or cls.dosave:
            Disk.write(cls.timers, cls.path)


def tmr(msg):
    "add a timer."
    if not msg.rest:
        msg.iface("<date> <txt>")
        return
    todo = Time.extract(msg.rest)
    if not todo:
        msg.reply("can't determine time")
        return
    todo += rand.random()
    if not todo or time.time() > todo:
        msg.reply("already passed given time.")
        return
    diff = todo - time.time()
    txt = " ".join(msg.args[1:])
    bot = Broker.get(msg.orig)
    TimerLoop.add(todo, Method.fqn(bot), msg.channel, txt)
    msg.ok(Time.elapsed(diff))
