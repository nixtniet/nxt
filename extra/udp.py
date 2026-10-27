# This file is placed in the Public Domain.


"UDP to IRC relay"


import select
import socket
import sys
import threading
import time


from nixt.defines import Clients, Log, Main, Object, Task


logger = Log(__name__)


def init():
    "initialize udp module."
    listener = UDP()
    listener.start()
    logger.warning("http://%s:%s", Cfg.host, Cfg.port)
    return listener


class Cfg(Object):

    "Configuration"

    addr = ""
    host = "localhost"
    port = 5500


class UDP(Object):

    "UDP listener"

    def __init__(self):
        Object.__init__(self)
        self.stopped = False
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.setblocking(True)
        self._starttime = time.time()
        self.ready = threading.Event()

    def exit(self):
        "quit UDP listener."
        self.stopped = True
        self._sock.settimeout(0.01)
        self._sock.sendto(
                          bytes("exit", "utf-8"),
                          (Cfg.host, Cfg.port)
                         )

    def loop(self):
        "udp loop."
        try:
            self._sock.bind((Cfg.host, Cfg.port))
        except socket.gaierror:
            return
        self.ready.set()
        while not self.stopped:
            (txt, addr) = self._sock.recvfrom(64000)
            if self.stopped:
                break
            data = str(txt.rstrip(), "utf-8")
            if not data:
                break
            self.output(data, addr)

    def output(self, txt, addr=None):
        "announce to clients."
        if addr:
            Cfg.addr = addr
        Clients.announce(txt.replace("\00", ""))

    def start(self):
        "start UDP listener."
        Task.start(self.loop)

    @classmethod
    def toudp(cls, host, port, txt):
        "send text to UDP relay."
        if Main.debug:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(bytes(txt.strip(), "utf-8"), (host, port))


def udp(msg):
    "senf text to UDP relay."
    if msg.rest:
        UDP.toudp(Cfg.host, Cfg.port, msg.rest)
        return
    if not select.select(
                         [sys.stdin, ],
                         [],
                         [],
                         0.0
                        )[0]:
        msg.iface("<text>")
        return
    size = 0
    while True:
        try:
            (inp, _out, err) = select.select(
                                             [sys.stdin,],
                                             [],
                                             [sys.stderr,]
                                            )
        except KeyboardInterrupt:
            return
        if err:
            break
        stop = False
        for sock in inp:
            txt = sock.readline()
            if not txt:
                stop = True
                break
            size += len(txt)
            UDP.toudp(Cfg.host, Cfg.port, txt)
        if stop:
            break
