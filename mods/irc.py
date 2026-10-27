# This file is placed in the Public Domain.


"internet relay chat"


import os
import socket
import ssl
import textwrap
import time
import _thread


from nixt.default import Event, Log, RLock, Queue
from nixt.defines import Broker, Buffer, Cfg, Commands, Disk, Main
from nixt.defines import Message, Mods, Method, Object, Task


logger = Log(__name__)


def init():
    "initialize irc module."
    irc = IRC()
    irc.start()
    try:
        irc.msgs.joined.wait(60.0)
    except (KeyboardInterrupt, EOFError):
        _thread.interrupt_main()
    if irc.msgs.joined.is_set():
        logger.info("%s", Method.fmt(irc.cfg, ["nick", "channel", "server", "port"]))
    else:
        irc.stop()
    return irc


class Config(Cfg):

    "IRC cofniguration"

    name = Main.name or Method.pkgname(Mods)
    channel = Main.channel or f"#{name}"
    commands = True
    control = "!"
    ignore = ["PING", "PONG", "PRIVMSG"]
    nick = name
    word = ""
    port = 6667
    realname = name
    sasl = port == 6697
    server = "localhost"
    servermodes = ""
    sleep = 60
    username = name
    users = False
    version = 1


class IRCEvent(Message):

    "IRC event"

    def __init__(self):
        super().__init__()
        self.args = []
        self.arguments = []
        self.command = ""
        self.channel = ""
        self.gets = {}
        self.nick = ""
        self.origin = ""
        self.rawstr = ""
        self.rest = ""
        self.sets = {}
        self.text = ""


class Events(Object):

    "IRC events."

    def __init__(self):
        super().__init__()
        self.authed: Event = Event()
        self.connected: Event = Event()
        self.joined: Event = Event()
        self.logon: Event = Event()
        self.ready: Event = Event()


class State(Object):

    "IRC state"

    def __init__(self):
        super().__init__()
        self.error = ""
        self.host = ""
        self.keeprunning = False
        self.last = time.time()
        self.latest = time.time()
        self.lastline = ""
        self.needconnect = False
        self.nickchange = 0
        self.nrconnect = 0
        self.nrerror = 0
        self.nrsend = 0
        self.pongcheck = False
        self.running = Event()
        self.stopkeep = False

class TextWrap(textwrap.TextWrapper):

    "wrap text into IRC protocol"

    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = False
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 400


wrapper = TextWrap()


class IRC(Buffer):

    "IYC client"

    def __init__(self):
        Buffer.__init__(self)
        self.buffer = []
        self.cfg = Config()
        self.channels = []
        self.msgs = Events()
        self.lock = RLock()
        self.noflood = True
        self.queue = Queue()
        self.silent = False
        self.sock = None
        self.state = State()
        self.register("903", cb_h903)
        self.register("904", cb_h903)
        self.register("AUTHENTICATE", cb_auth)
        self.register("CAP", cb_cap)
        self.register("ERROR", cb_error)
        self.register("LOG", cb_log)
        self.register("NOTICE", cb_notice)
        self.register("PRIVMSG", cb_privmsg)
        self.register("QUIT", cb_quit)
        self.register("366", cb_ready)
        self.zelf = ""

    def announce(self, text):
        "announce test on all joined channels."
        for channel in self.channels:
            self.say(channel, text)

    def connect(self, server, port=6667):
        "connect to irc server."
        self.state.nrconnect += 1
        self.msgs.connected.clear()
        self.msgs.joined.clear()
        if self.cfg.word or self.cfg.word:
            logger.debug("using SASL")
            self.cfg.sasl = True
            self.cfg.port = 6697
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = ctx.wrap_socket(sock)
            self.sock.connect((server, port))
            self.direct("CAP LS 302")
        else:
            addr = socket.getaddrinfo(server, port, socket.AF_INET)[-1][-1]
            host, port = addr[:2]
            addr2 = (str(host), int(port))
            self.sock = socket.create_connection(addr2)
            self.msgs.authed.set()
        if self.sock:
            os.set_inheritable(self.sock.fileno(), True)
            self.sock.setblocking(True)
            self.sock.settimeout(180.0)
            self.msgs.connected.set()
            logger.debug(
                      "connected %s:%s channel %s",
                      self.cfg.server,
                      self.cfg.port,
                      self.cfg.channel
                     )
            return True
        return False

    def direct(self, txt):
        "write directly on the socket with a 2 sec interval."
        with self.lock:
            time.sleep(2.0)
            self.raw(txt)

    def disconnect(self):
        "disconnect from server."
        try:
            if self.sock:
                self.sock.shutdown(2)
        except (ssl.SSLError, OSError, BrokenPipeError):
            pass

    def display(self, msg):
        "display results of an msg."
        if len(msg.result) > 3:
            self.say(msg.channel, "command would flood")
            return
        for txt in msg.result:
            for text in wrapper.wrap(txt):
                self.dosay(msg.channel, text)
        msg.ready()

    def docommand(self, cmd, *args):
        "basic commands."
        with self.lock:
            if not args:
                self.raw(cmd)
            elif len(args) == 1:
                self.raw(f"{cmd.upper()} {args[0]}")
            elif len(args) == 2:
                txt = " ".join(args[1:])
                self.raw(f"{cmd.upper()} {args[0]} :{txt}")
            elif len(args) >= 3:
                txt = " ".join(args[2:])
                self.raw(f"{cmd.upper()} {args[0]} {args[1]} :{txt}")
            if (time.time() - self.state.last) < 5.0:
                time.sleep(5.0)
            self.state.last = time.time()

    def doconnect(self):
        "loop until connected."
        while True:
            try:
                if self.connect(self.cfg.server, self.cfg.port):
                    self.logon(self.cfg.server, self.cfg.nick)
                    self.msgs.joined.wait(45.0)
                    if not self.msgs.joined.is_set():
                        self.disconnect()
                        self.msgs.joined.set()
                        continue
                    break
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()
            except (
                    TimeoutError,
                    ssl.SSLError,
                    OSError,
                    ConnectionResetError
                   ) as ex:
                self.msgs.joined.set()
                self.state.error = str(ex)
                logger.debug("%s", str(type(ex)) + " " + str(ex))
            time.sleep(self.cfg.sleep)

    def dosay(self, channel, text):
        "sanitize before sending text to a channel."
        self.msgs.joined.wait()
        txt = str(text).replace("\n", "")
        txt = txt.replace("  ", " ")
        self.docommand("PRIVMSG", channel, txt)
        del txt

    def msg(self, txt):
        "parse text into an msg."
        msg = self.parsing(txt)
        cmd = msg.command
        if cmd == "PING":
            self.state.pongcheck = True
            self.docommand("PONG", msg.text or "")
        elif cmd == "PONG":
            self.state.pongcheck = False
        if cmd == "001":
            self.state.needconnect = False
            if self.cfg.servermodes:
                self.docommand(f"MODE {self.cfg.nick} {self.cfg.servermodes}")
            self.zelf = msg.args[-1]
        elif cmd == "376":
            self.joinall()
        elif cmd == "002":
            self.state.host = msg.args[2][:-1]
        elif cmd == "366":
            self.state.error = ""
            self.msgs.joined.set()
        elif cmd == "433":
            self.state.error = txt
            self.state.nickchange += 1
            nck = self.cfg.nick + ("_" * self.state.nickchange)
            self.docommand("NICK", nck)
        return msg

    def joinall(self):
        "join all chennels."
        for channel in self.channels:
            self.docommand("JOIN", channel)

    def keep(self):
        "keep alive loop."
        while not self.stopped.is_set():
            if self.state.stopkeep:
                self.state.stopkeep = False
                break
            self.msgs.connected.wait()
            self.msgs.authed.wait()
            self.state.keeprunning = True
            self.state.latest = time.time()
            for _x in range(self.cfg.sleep*10):
                time.sleep(0.1)
                if self.stopped.is_set():
                    break
            self.docommand("PING", self.cfg.server)
            if self.state.pongcheck:
                self.restart()

    def logon(self, server, nck):
        "log onto the irc network."
        self.msgs.connected.wait()
        self.msgs.authed.wait()
        self.direct(f"NICK {nck}")
        self.direct(f"USER {nck} {server} {server} {nck}")

    def oput(self, msg):
        "put msg onto output queue."
        self.oqueue.put_nowait(msg)

    def parsing(self, txt):
        "parse text into an msg."
        rawstr = str(txt)
        rawstr = rawstr.replace("\u0001", "")
        rawstr = rawstr.replace("\001", "")
        self.rlog(txt)
        obj = IRCEvent()
        obj.args = []
        obj.rawstr = rawstr
        obj.command = ""
        obj.arguments = []
        arguments = rawstr.split()
        if arguments:
            obj.origin = arguments[0]
        else:
            obj.origin = self.cfg.server
        if obj.origin.startswith(":"):
            obj.origin = obj.origin[1:]
            if len(arguments) > 1:
                obj.command = arguments[1]
                obj.kind = obj.command
            if len(arguments) > 2:
                txtlist = []
                adding = False
                for arg in arguments[2:]:
                    if arg.count(":") <= 1 and arg.startswith(":"):
                        adding = True
                        txtlist.append(arg[1:])
                        continue
                    if adding:
                        txtlist.append(arg)
                    else:
                        obj.arguments.append(arg)
                obj.text = " ".join(txtlist)
        else:
            obj.command = obj.origin
            obj.origin = self.cfg.server
        try:
            obj.nick, obj.origin = obj.origin.split("!")
        except ValueError:
            obj.nick = ""
        todo = ""
        if obj.arguments:
            todo = obj.arguments[0]
        if todo.startswith("#"):
            obj.channel = todo
        else:
            obj.channel = obj.nick
        return self.post(obj, rawstr, arguments)


    def poll(self):
        "poll on the socket for an msg."
        self.msgs.connected.wait()
        if not self.buffer:
            try:
                self.some()
            except BlockingIOError as ex:
                time.sleep(1.0)
                return self.msg(str(ex))
            except (
                TimeoutError,
                OSError,
                ssl.SSLError,
                ssl.SSLZeroReturnError,
                ConnectionResetError,
                BrokenPipeError,
            ) as ex:
                self.state.nrerror += 1
                self.state.error = str(type(ex)) + " " + str(ex)
                logger.debug(self.state.error)
                self.state.pongcheck = True
                self.stop()
                return None
        try:
            txt = self.buffer.pop(0)
        except IndexError:
            txt = ""
        self.put(self.msg(txt))
        return None

    def post(self, obj, rawstr, arguments):
        "post parsing."
        if not obj.text:
            obj.text = rawstr.split(":", 2)[-1]
        if not obj.text and len(arguments) == 1:
            obj.text = arguments[1]
        splitted = obj.text.split()
        if len(splitted) > 1:
            obj.args = splitted[1:]
        if obj.args:
            obj.rest = " ".join(obj.args)
        obj.orig = repr(self)
        obj.text = obj.text.strip()
        obj.kind = obj.command
        return obj

    def raw(self, text):
        "raw output to the server."
        text = text.rstrip()
        self.rlog(text)
        text = text[:500]
        text += "\r\n"
        text = bytes(text, "utf-8")
        if self.sock:
            try:
                self.sock.send(text)
            except (
                TimeoutError,
                OSError,
                ssl.SSLError,
                ssl.SSLZeroReturnError,
                ConnectionResetError,
                BrokenPipeError,
            ) as ex:
                logger.debug("%s", str(type(ex)) + " " + str(ex))
                self.msgs.joined.set()
                self.state.nrerror += 1
                self.state.error = str(ex)
                self.state.pongcheck = True
                self.stop()
                return
        self.state.last = time.time()
        self.state.nrsend += 1

    def reconnect(self):
        "reconnect to server."
        logger.debug("reconnecting %s:%s", self.cfg.server, self.cfg.port)
        self.disconnect()
        self.msgs.connected.clear()
        self.msgs.joined.clear()
        self.doconnect()

    def restart(self):
        "restart client."
        logger.debug("restart")
        self.msgs.joined.set()
        self.state.pongcheck = False
        self.state.keeprunning = False
        self.state.stopkeep = True
        self.stop()
        Task.start(init)

    def rlog(self, txt):
        "log function that ignore ping/pong/etc."
        for ign in Config.ignore:
            if ign in str(txt):
                return
        logger.debug(txt)

    def say(self, channel, text):
        "say text in the channel."
        msg = IRCEvent()
        msg.channel = channel
        msg.reply(text)
        self.oput(msg)

    def some(self):
        "read some text from the socket."
        self.msgs.connected.wait()
        if not self.sock:
            return
        inbytes = self.sock.recv(512)
        text = str(inbytes, "utf-8")
        if text == "":
            raise ConnectionResetError
        self.state.lastline += text
        splitted = self.state.lastline.split("\r\n")
        for line in splitted[:-1]:
            self.buffer.append(line)
        self.state.lastline = splitted[-1]

    def start(self, daemon=True):
        "start client."
        Disk.read(self.cfg, "irc", "config")
        if self.cfg.channel not in self.channels:
            self.channels.append(self.cfg.channel)
        self.msgs.connected.clear()
        self.msgs.joined.clear()
        self.msgs.ready.clear()
        Buffer.start(self)
        if not self.state.keeprunning:
            Task.start(self.keep, daemon=daemon)
        Task.start(self.doconnect)

    def stop(self):
        "stop client."
        self.state.stopkeep = True
        Buffer.stop(self)

    def wait(self):
        "wait for client to join."
        try:
            self.msgs.ready.wait()
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


def cb_auth(msg):
    "authorisation callback."
    bot = Broker.get(msg.orig)
    bot.docommand(f"AUTHENTICATE {bot.cfg.word}")


def cb_cap(msg):
    "capabilities callback."
    bot = Broker.get(msg.orig)
    if (bot.cfg.word or bot.cfg.word and "ACK" in msg.arguments):
        bot.direct("AUTHENTICATE PLAIN")
    else:
        bot.direct("CAP REQ :sasl")


def cb_error(msg):
    "error callback."
    bot = Broker.get(msg.orig)
    bot.state.nrerror += 1
    bot.state.error = msg.text
    logger.debug(Method.fmt(msg))


def cb_h903(msg):
    "end capabilities callback."
    bot = Broker.get(msg.orig)
    bot.direct("CAP END")
    bot.msgs.authed.set()


def cb_h904(msg):
    "end capabilities callback."
    bot = Broker.get(msg.orig)
    bot.direct("CAP END")
    bot.msgs.authed.set()


def cb_kill(msg):
    "kill callback."


def cb_log(msg):
    "log callbacl."


def cb_ready(msg):
    "ready callback."
    bot = Broker.get(msg.orig)
    bot.msgs.ready.set()


def cb_001(msg):
    "greeting callback."
    bot = Broker.get(msg.orig)
    bot.msgs.logon.set()


def cb_notice(msg):
    "notice callback."
    bot = Broker.get(msg.orig)
    if msg.text.startswith("VERSION"):
        name = Config.name.upper()
        ver = Config.version
        user = bot.cfg.username
        txt = f"\001VERSION {name} {ver} - {user}\001"
        bot.docommand("NOTICE", msg.channel, txt)


def cb_privmsg(msg):
    "privmsg callback."
    bot = Broker.get(msg.orig)
    if not bot.cfg.commands:
        return
    if msg.text:
        if msg.text[0] == bot.cfg.control:
            msg.text = msg.text[1:]
        elif msg.text.startswith(f"{bot.cfg.nick}:"):
            msg.text = msg.text[len(bot.cfg.nick) + 1:]
        else:
            return
        if msg.text:
            msg.text = msg.text[0].lower() + msg.text[1:]
        if msg.text:
            name = msg.text and msg.text.split()[0]
            Task.start(Commands.command, msg, name=name)


def cb_quit(msg):
    "qiot callback."
    bot = Broker.get(msg.orig)
    logger.debug("quit from %s", bot.cfg.server)
    bot.state.nrerror += 1
    bot.state.error = msg.text
    if msg.orig and msg.orig in bot.zelf:
        bot.stop()


def pwd(msg):
    "generate sasl password."
    if len(msg.args) != 2:
        msg.iface("<nick> <password>")
        return
    import base64
    arg1 = msg.args[0]
    arg2 = msg.args[1]
    txt = f"\x00{arg1}\x00{arg2}"
    enc = txt.encode("ascii")
    base = base64.b64encode(enc)
    dcd = base.decode("ascii")
    msg.reply(dcd)
