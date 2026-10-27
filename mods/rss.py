# This file is placed in the Public Domain.


"rich site syndicate"


import gc
import html
import logging.handlers
import os
import pathlib
import re
import urllib.parse


from urllib.parse   import unquote, urlparse, urlunparse
from urllib.request import Request, urlopen


from nixt.default import Log, RLock
from nixt.defines import Cfg, Clients, Data, Disk, Format, JSON, JSONL, Locater
from nixt.defines import Logging, Main, MD5, Method, Object, Pool, Repeater
from nixt.defines import Runner, Utils, Watcher, Workdir


logger = Log(__name__)


def init():
    "initialize rss module."
    Disk.read(Config, "rss", "config")
    Run.start()
    nrs = Locater.count("rss")
    txt = f"{nrs} feeds"
    if nrs == 1:
        txt = txt[:-1]
    logger.info(txt)


def shutdown():
    "shutdown rss module."
    Run.stop()


class Config(Cfg):

    "configuration"

    polltime = 300
    save = False


class Feed(Data):

    "feed data"


class Response(Data):

    "response object"

    def __init__(self):
        Data.__init__(self)
        self.data = b""
        self.reason = ""
        self.status = None
        self.url = ""


class Rss(Data):

    "feed meta data"

    def __init__(self):
        super().__init__()
        self.__deleted__ = False
        self.display_list = "title,link,author"
        self.error = ""
        self.feed = ""
        self.insertid = ""
        self.name = ""
        self.rss  = ""
        self.seen = []
        self.size = 0
        self.skip = False
        self.status = 0


class State(Object):

    "keeping state"

    index = 0


class Locks:

    "locking"

    importlock = RLock()


class Run:

    "runtime"

    path = ""
    file = None
    lock = RLock()
    configfn = ""
    modifiedfn = ""
    statefn = ""
    index = 0

    @classmethod
    def callback(cls):
        "monitor log file."
        if cls.file is None:
            return
        with cls.lock:
            cls.file.seek(State.index, 0)
            while True:
                line = cls.file.readline()
                if not line:
                    break
                feed = Feed()
                Method.construct(feed, JSONL.loads(line.strip()))
                txt = cls.display(feed)
                if not Run.got(txt, feed):
                    Clients.announce(txt)
            State.index = cls.file.tell()
        Disk.write(State, cls.statefn)
        gc.collect(0)

    @classmethod
    def clear(cls):
        "retry all failed feeds."
        counter = 0
        for fnm, feed in Locater.find(Method.fqn(Rss)):
            if feed.skip:
                feed.skip = False
                Disk.write(feed, fnm)
                counter += 1
        logger.debug("clear %s", counter)
        return counter

    @classmethod
    def display(cls, obj, name=None):
        "display feed."
        displaylist = ""
        if name in obj:
            result = f"[{obj.name}] "
        else:
            result = ""
        try:
            displaylist = Method.get(obj, "display_list") or "title,link"
        except AttributeError:
            displaylist = "title,link,author"
        for key in displaylist.split(","):
            if not key:
                continue
            data = Method.get(obj, key, None)
            if not data:
                continue
            stripped = Fetcher.striphtml(data.replace("\n", " ").rstrip())
            result += Fetcher.unescape(stripped)
            result += " - "
        return result[:-2].rstrip()

    @classmethod
    def enable(cls, path):
        "enabke module logger."
        formatter = Format(Logging.formats, Logging.datefmt)
        filehandler = logging.handlers.TimedRotatingFileHandler(path, 'midnight')
        filehandler.setFormatter(formatter)
        if logger.handlers:
            for handler in logger.handlers:
                logger.removeHandler(handler)
        logger.addHandler(filehandler)
        logger.propagate = False
        logger.setLevel("DEBUG")

    @classmethod
    def got(cls, text, feed):
        "verify whether text has already been seen."
        md5 = MD5.source(text)[:7]
        if md5 in feed.seen:
            return True
        feed.seen.insert(0, md5)
        return False

    @classmethod
    def log(cls, text):
        "log to file."
        logger.debug(text)

    @classmethod
    def run(cls, silent=False):
        "do a fetch run of all feeds."
        nrs = 0
        if Pool.busy():
            logger.debug("next!")
            return 0
        for fnm, feed in Locater.find(Method.fqn(Rss)):
            if feed.skip:
                continue
            Pool.put((fnm, feed, silent))
            nrs += 1
        return nrs

    @classmethod
    def start(cls, once=False):
        "initialise module."
        if Config.save:
            cls.path = os.path.join(Workdir.logdir("rss"), 'rss.log')
            Utils.cdir(cls.path)
            pathlib.Path(cls.path).touch()
            with open(cls.path, "a+", encoding="utf-8") as file:
                cls.file = file
            cls.enable(cls.path)
            Watcher.add(cls.path, cls.callback)
            Watcher.start()
        cls.statefn = Locater.last(State) or Disk.ident(State)
        Pool.init(2, Fetching)
        if not once:
            Repeater.add(Config.polltime, cls.run)
            Repeater.add(7200, cls.clear)
            Repeater.start()

    @classmethod
    def stop(cls):
        "shutdown."
        Watcher.stop()

    @classmethod
    def sync(cls):
        "sync state to disk."
        if cls.index > State.index:
            State.index = cls.index
            Disk.write(State, cls.statefn)


class Fetching(Runner):

    "teh fetcher"

    def __init__(self):
        Runner.__init__(self)

    def doskip(self, errno):
        "check whether to log."
        return errno >= 400

    def getfeed(self, fnm, feed, items):
        "fetch a feed."
        response = Fetcher.geturl(feed.rss)
        if not response.data:
            if response.status and self.doskip(response.status):
                feed.status = response.status
                feed.error = response.error
                feed.skip = True
                Disk.write(feed, fnm)
                logger.warning("skipt %s %s %s", feed.rss, response.status, response.reason)
            yield Feed()
        else:
            logger.debug("fetch %s", feed.rss)
            if "link" not in items:
                items += ",link"
            yield from RSS.parse(
                                 str(response.data, "utf-8", errors='ignore'),
                                 (feed.rss.endswith("atom") and "entry") or "item",
                                 items
                                ) or []

    def run(self, *args, **kwargs):
        "poll all feeds."
        counter = 0
        try:
            fnm, feed, silent = args
        except ValueError:
            return counter
        if not feed.seen:
            feed.seen = []
        has = False
        gotcha = 0
        for obj in self.getfeed(fnm, feed, feed.display_list):
            counter += 1
            if obj is None:
                continue
            if Method.isempty(obj):
                continue
            Method.update(obj, feed)
            if Config.save:
                Run.log(JSON.dumps(feed))
            if not silent:
                txt = Run.display(obj)
                if not Run.got(txt, obj):
                    Clients.announce(txt)
                    gotcha += 1
                    has = True
            del obj
        if has:
            feed.seen = feed.seen[:counter]
            Disk.write(feed, fnm)
            logger.debug("write %s (%s)", feed.rss, gotcha)
        if counter:
            gc.collect(0)
        return counter


class Fetcher:

    "fetch urls"

    modified = {}

    @classmethod
    def cdata(cls, line):
        "scrape CDATA block."
        if "CDATA" in line:
            lne = line.replace("![CDATA[", "")
            lne = lne.replace("]]", "")
            lne = lne[1:-1]
            return lne
        return line

    @classmethod
    def geturl(cls, url):
        "fetch an url."
        url = urlunparse(urlparse(url))
        req = Request(str(url))
        req.add_header("User-Agent", cls.useragent(f"{Main.name.upper()} {MD5.core()}"))
        since = cls.modified.get(url, "")
        if since:
            req.add_header('If-Modified-Since', since)
        response = Response()
        response.url = url
        response.reason = ""
        try:
            Method.update(response, cls.request(req))
        except Exception as ex:
            # pylint: disable=E1101
            response.data = b""
            if "reason" in dir(ex):
                response.reason = ex.reason # type: ignore
            else:
                response.reason = str(ex)
            if "status" in dir(ex):
                response.status = ex.status # type: ignore
            else:
                response.status = None
        return response

    @classmethod
    def request(cls, req):
        "handle  a request."
        with urlopen(req, timeout=4) as response:  # nosec
            modi = response.headers.get('Last-Modified', "")
            if modi:
                cls.modified[req.get_full_url()] = modi
            response.data = response.read()
            response.error = ""
            return response

    @classmethod
    def striphtml(cls, text):
        "strip html."
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    @classmethod
    def unescape(cls, text):
        "unescape html."
        txt = re.sub(r"\s+", " ", text)
        return html.unescape(txt)

    @classmethod
    def unquote(cls, url):
        "unquote an url."
        return unquote(url, errors='ignore')

    @classmethod
    def useragent(cls, text):
        "produce useragent string."
        return "Mozilla/5.0 (X11; Linux x86_64) " + text


class OPML:

    "opml parser"

    @classmethod
    def getnames(cls, line):
        "get names from line."
        return [x.split('="')[0] for x in line.split()]

    @classmethod
    def getvalue(cls, line, attr):
        "get value from line."
        lne = ""
        index1 = line.find(f'{attr}="')
        if index1 == -1:
            return lne
        index1 += len(attr) + 2
        index2 = line.find('"', index1)
        if index2 == -1:
            index2 = line.find("/>", index1)
        if index2 == -1:
            return lne
        return Fetcher.cdata(line[index1:index2])

    @classmethod
    def getattrs(cls, line, token):
        "get attributes from line."
        index = 0
        result = []
        stop = False
        while not stop:
            index1 = line.find(f"<{token} ", index)
            if index1 == -1:
                return result
            index1 += len(token) + 2
            index2 = line.find("/>", index1)
            if index2 == -1:
                return result
            result.append(line[index1:index2])
            index = index2
        return result

    @classmethod
    def parse(cls, txt, toke="outline", itemz=None):
        "parse opml from text."
        if itemz is None:
            itemz = ",".join(cls.getnames(txt))
        for attrz in cls.getattrs(txt, toke):
            if not attrz:
                continue
            obj = {}
            for itm in Utils.spl(itemz):
                if itm == "link":
                    itm = "href"
                obj[itm] = cls.getvalue(attrz, itm)
            yield obj


class RSS:

    "RSS parser"

    @classmethod
    def getitem(cls, line, item):
        "return item from line."
        lne = ""
        index1 = line.find(f"<{item}>")
        if index1 == -1:
            return lne
        index1 += len(item) + 2
        index2 = line.find(f"</{item}>", index1)
        if index2 == -1:
            return lne
        return Fetcher.cdata(line[index1:index2]).strip()

    @classmethod
    def getitems(cls, text, token, nrs=0):
        "get items from text."
        index = 0
        end = len(text)
        stop = False
        nrx = -1
        while not stop:
            nrx += 1
            if nrs and nrx >= nrs:
                break
            index1 = text.rfind(f"<{token}", index, end)
            if index1 == -1:
                break
            end = index1
            index1 += len(token) + 2
            index2 = text.rfind(f"</{token}>", index1)
            if index2 == -1:
                break
            yield text[index1:index2]

    @classmethod
    def parse(cls, txt, toke="item", items="title,link"):
        "parse feed."
        for line in cls.getitems(txt, toke):
            line = line.strip()
            feed = Feed()
            for itm in Utils.spl(items):
                val = cls.getitem(line, itm)
                if val:
                    escaped = Fetcher.unescape(val.strip())
                    feed[itm] = Fetcher.striphtml(escaped).replace("\n", "")
            yield feed


def atr(msg):
    "show attributes of a feed."
    if not msg.rest:
        msg.iface("<stringinurl>")
        return
    for obj in Locater.objects(Method.fqn(Rss), {'rss': msg.rest}):
        request = Fetcher.geturl(obj.rss)
        if not request:
            continue
        if obj.rss.endswith('atom'):
            result = list(RSS.getitems(
                                       str(request.data, 'utf-8', errors='ignore'),
                                       'entry',
                                       1
                                      ))
        else:
            result = list(RSS.getitems(
                                       str(request.data, 'utf-8', errors='ignore'),
                                       'item',
                                       1
                                      ))
        resulting = []
        for x in re.findall('<.*?>', result[0]):
            if x[1] == '/' and len(x) > 4:
                resulting.append(x[2:-1])
        msg.reply(','.join(resulting))


def dpl(msg):
    "set feed items to display."
    if len(msg.args) < 2:
        msg.iface("<stringinurl> <item1,item2>")
        return
    setter = {"display_list": msg.args[1]}
    for fnm, feed in Locater.find(Method.fqn(Rss), {"rss": msg.args[0]}):
        if feed:
            Method.update(feed, setter)
            Disk.write(feed, fnm)
    msg.ok()


def exp(msg):
    "export opml."
    with Locks.importlock:
        msg.reply(TEMPLATE)
        for nrs, ooo in enumerate(Locater.objects(Method.fqn(OPML))):
            obj = Rss()
            Method.update(obj, ooo)
            name = f"url{nrs}"
            dipl = obj.display_list
            url = obj.rss
            txt = f'<outline name="{name}" display_list="{dipl}" xmlUrl="{url}"/>'
            msg.reply(" " * 12 + txt)
        msg.reply(" " * 8 + "</outline>")
        msg.reply("    <body>")
        msg.reply("</opml>")


def imp(msg):
    "import opml."
    if not msg.args:
        msg.iface("<filename>")
        return
    fnm = msg.args[0]
    if not os.path.isfile(fnm):
        msg.reply(f"no {fnm} file found.")
        return
    with Locks.importlock:
        with open(fnm, "r", encoding="utf-8") as file:
            txt = file.read()
        prs = OPML()
        nrs = 0
        nrskip = 0
        insertid = Utils.shortid()
        skipped = []
        for obj in prs.parse(txt, "outline", "name,xmlUrl"):
            url = obj["xmlUrl"]
            if url in skipped:
                continue
            if not url.startswith("http"):
                continue
            has = list(Locater.find(
                                   Method.fqn(OPML),
                                   {"rss": url},
                                   matching=True
                                  ))
            if has:
                skipped.append(url)
                nrskip += 1
                continue
            feed = Rss()
            feed.rss = obj["xmlUrl"]
            del obj["xmlUrl"]
            Method.update(feed, obj)
            uri = urllib.parse.urlparse(feed.rss)
            feed.name = str(max(uri.netloc.split("."), key=len))
            feed.insertid = insertid
            Disk.write(feed)
            nrs += 1
    if nrskip:
        msg.reply(f"skipped {nrskip} urls.")
    if nrs:
        msg.reply(f"added {nrs} urls.")


def nme(msg):
    "set name of a feed."
    if len(msg.args) == 1:
        name = ""
    elif len(msg.args) == 2:
        name = msg.args[1]
    else:
        msg.iface("<stringinurl> <name>")
        return
    selector = {"rss": msg.args[0]}
    for fnm, fed in Locater.find(
                                Method.fqn(Rss),
                                selector
                               ):
        feed = Rss()
        Method.update(feed, fed)
        if feed:
            feed.name = name
            Disk.write(feed, fnm)
    msg.ok()


def rem(msg):
    "remove a feed."
    if len(msg.args) != 1:
        msg.iface("<stringinurl>")
        return
    for fnm, fed in Locater.find(Method.fqn(Rss)):
        feed = Rss()
        Method.update(feed, fed)
        if msg.args[0] not in feed.rss:
            continue
        if feed:
            feed.__deleted__ = True
            Disk.write(feed, fnm)
            msg.ok()
            break


def res(msg):
    "restore a feed."
    if len(msg.args) != 1:
        msg.iface("<stringinurl>")
        return
    nrs = 0
    for fnm, fed in Locater.find(
                                Method.fqn(Rss),
                                removed=True
                               ):
        feed = Rss()
        Method.update(feed, fed)
        if msg.args[0] not in feed.rss:
            continue
        nrs += 1
        feed.__deleted__ = False
        feed.skip = False
        Disk.write(feed, fnm)
    msg.reply(f"{nrs} feeds restored.")


def rss(msg):
    "add a feed."
    if not msg.rest:
        msg.iface("<url>")
        return
    url = msg.args[0]
    if "http://" not in url and "https://" not in url:
        msg.reply("i need an url")
        return
    for result in Locater.objects(Method.fqn(Rss), {"rss": url}):
        if result:
            msg.reply(f"{url} is known")
            return
    feed = Rss()
    feed.rss = msg.args[0]
    Disk.write(feed)
    msg.ok()


def syn(msg):
    "synchronize a feed."
    if Main.debug:
        return
    nrs = Run.run(True)
    cleared = Run.clear()
    msg.reply(f"{nrs} feeds synced {cleared} cleared")


TEMPLATE = """<opml version="1.0">
    <head>
        <title>OPML</title>
    </head>
    <body>
        <outline title="opml" text="rss feeds">"""
