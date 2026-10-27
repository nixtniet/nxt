# This file is placed in the Public Domain.


"usefulness"


import os
import time
import uuid


from datetime import datetime


from .default import Formatter, Log, Path, StreamHandler
from .default import TimedRotatingFileHandler, basicConfig


logger = Log(__name__)


class Format(Formatter):

    "logging format"

    disable = False
    size = 3

    def format(self, record):
        "logging formatter."
        if not Format.disable:
            record.module = record.module.upper()
            record.module = record.module[:Format.size]
        return Formatter.format(self, record)


class Logging:

    "log"

    datefmt = "%H:%M:%S"
    format = "%(module)-3s %(message)s"
    formats = "%(message)s"

    @classmethod
    def enable(cls, path, log):
        "enabke module logger."
        formatter = Format(Logging.formats, Logging.datefmt)
        filehandler = TimedRotatingFileHandler(path, 'midnight')
        filehandler.setFormatter(formatter)
        if log.handlers:
            for handler in log.handlers:
                log.removeHandler(handler)
        log.addHandler(filehandler)
        log.propagate = False
        log.setLevel("DEBUG")

    @classmethod
    def level(cls, loglevel):
        "set log level."
        formatter = Format(cls.formats, cls.datefmt)
        stream = StreamHandler()
        stream.setFormatter(formatter)
        try:
            basicConfig(
                level=loglevel.upper(),
                handlers=[stream],
                force=True
            )
        except ValueError:
            pass

    @classmethod
    def size(cls, nrchars):
        "set text size."
        index = cls.format.find("-")+1
        newformat = cls.format[:index]
        newformat += str(nrchars)
        newformat += cls.format[index+1:]
        cls.format = newformat


class MD5:

    "module md5sum"

    @classmethod
    def check(cls, md5s):
        "check for md5sums in a given path."
        ok = True
        if not __spec__:
            return ok
        path = os.path.dirname(str(__spec__.origin))
        if not os.path.exists(path):
            return False
        for pth in os.listdir(path):
            if pth.startswith("__") or not pth.endswith(".py") or "statics" in pth:
                continue
            name = pth[:-3]
            modpath = os.path.join(path, pth)
            if md5s and cls.md5(modpath) != md5s.get(name):
                logger.warning("mismatch %s", name)
                ok = False
        return ok

    @classmethod
    def core(cls):
        "calculate md5 of the statics module."
        try:
            from . import statics
        except (ModuleNotFoundError, ImportError, SyntaxError):
            return ""
        txt = Utils.source(statics)
        if txt:
            return cls.source(txt)[:7].upper()
        return None

    @classmethod
    def createmd5(cls, path, data):
        "create md5s for file in a directory."
        for pth in os.listdir(path):
            if pth.startswith("__") or not pth.endswith(".py") or "statics" in pth:
                continue
            name = pth[:-3]
            data[name] = cls.md5(os.path.join(path, pth))

    @classmethod
    def md5(cls, path):
        "calculate md5sum of a file."
        if not os.path.exists(path):
            return ""
        import hashlib
        md5s = hashlib.md5()
        with open(path, "r", encoding="utf-8") as file:
            md5s.update(file.read().encode("utf-8"))
        return str(md5s.hexdigest())

    @classmethod
    def source(cls, src):
        "determine md5 of source code."
        import hashlib
        md5 = hashlib.md5()
        md5.update(src.encode("utf-8"))
        return str(md5.hexdigest())


class Time:

    "time related utilities"

    starttime = time.time()
    times = (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S",
        "%a, %d %b %Y %T %z",
        "%a, %d %b %Y %T",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d-%m",
        "%m-%d"
    )

    @classmethod
    def date(cls, daystr):
        "date from string."
        daystr = daystr.encode('utf-8', 'replace').decode("utf-8")
        for fmat in cls.times:
            try:
                return time.mktime(time.strptime(daystr, fmat))
            except ValueError:
                pass
        return None

    @classmethod
    def elapsed(cls, seconds, short=True):
        "seconds to string."
        txt = ""
        nsec = float(seconds)
        if nsec < 1:
            return f"{nsec:.2f}s"
        yea = 365 * 24 * 60 * 60
        week = 7 * 24 * 60 * 60
        nday = 24 * 60 * 60
        hou = 60 * 60
        minute = 60
        yeas = int(nsec / yea)
        nsec -= yeas * yea
        weeks = int(nsec / week)
        nsec -= weeks * week
        nrdays = int(nsec / nday)
        nsec -= nrdays * nday
        hours = int(nsec / hou)
        nsec -= hours * hou
        minutes = int(nsec / minute)
        nsec -= minutes * minute
        sec = int(nsec / 1)
        nsec -= nsec - sec
        if yeas:
            txt += f"{yeas}y"
        if weeks:
            nrdays += weeks * 7
        if nrdays:
            txt += f"{nrdays}d"
        if hours:
            txt += f"{hours}h"
        if short and txt:
            return txt.strip()
        if minutes:
            txt += f"{minutes}m"
        if sec:
            txt += f"{sec}s"
        txt = txt.strip()
        return txt

    @classmethod
    def extract(cls, daystr):
        "extract date/time from string."
        daystr = str(daystr)
        res = None
        for word in daystr.split():
            if word.startswith("+"):
                try:
                    return int(word[1:]) + time.time()
                except (ValueError, IndexError):
                    continue
            res = cls.date(word.strip())
            if not res:
                date = datetime.fromtimestamp(time.time(), tz=None).date()
                word = f"{date.year}-{date.month}-{date.day}" + " " + word
                res = cls.date(word.strip())
            if res:
                break
        return res

    @classmethod
    def timed(cls, datestr):
        "return time from string."
        tme = cls.date(datestr)
        if not tme:
            tme = time.time()
        return tme


class Utils:

    "useful functions"

    @staticmethod
    def cdir(path):
        "create directory."
        if os.path.exists(path):
            return
        pth = Path(path)
        if not os.path.exists(pth.parent):
            pth.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def clsname(obj):
        "return classname of an object."
        return obj.__class__.__name__

    @staticmethod
    def funcname(obj):
        "return functionname."
        try:
            return obj.__name__
        except AttributeError:
            return ""

    @staticmethod
    def home(name):
        "return home working directory."
        return os.path.expanduser(f"~/.{name}")

    @staticmethod
    def listdir(path, ignore=""):
        "list modules in a directory."
        return [
                x[:-3] for x in os.listdir(path)
                if x.endswith(".py") and
                not x.startswith("__") and
                x[:-3] not in Utils.spl(ignore)
               ]

    @staticmethod
    def shortid():
        "return a shortid."
        return str(uuid.uuid4())[:8]

    @staticmethod
    def source(module):
        "return the source of a module."
        if module.__spec__ is None:
            return None
        if module.__spec__.loader is None:
            return None
        get = getattr(module.__spec__.loader, "get_source", None)
        if get:
            return get(module.__name__)
        return None

    @staticmethod
    def spl(text, ignore=""):
        "list from comma seperated string."
        try:
            ignores = ignore.split(",")
            result = text.split(",")
        except (TypeError, ValueError):
            result = []
        return [x for x in result if x and x not in ignores]

    @staticmethod
    def strip(path, nrchar=3):
        "strip filename from path."
        return os.path.join(*path.split(os.sep)[-nrchar:])


def __dir__():
    return (
        'MSS',
        'Format',
        'Logging',
        'Time',
        'Utils'
    )
