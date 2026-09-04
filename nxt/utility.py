# This file is placed in the Public Domain.


"usefulness"


import datetime
import inspect
import logging
import logging.handlers
import html
import os
import pathlib
import re
import time
import urllib
import uuid


j = os.path.join


class Format(logging.Formatter):

    disable = False
    size = 3

    def format(self, record):
        "logging formatter."
        if not Format.disable:
            record.module = record.module.upper()
            record.module = record.module[:Format.size]
        return logging.Formatter.format(self, record)


class Logging:

    datefmt = "%H:%M:%S"
    format = "%(module)-3s %(message)s"
    formats = "%(message)s"
    
    @classmethod
    def level(cls, loglevel, systemd=False):
        "set log level."
        formatter = Format(cls.format, cls.datefmt)
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        logging.basicConfig(
            level=loglevel.upper(),
            handlers=[stream],
            force=True
        )

    @classmethod
    def size(cls, nr):
        "set text size."
        index = cls.format.find("-")+1
        newformat = cls.format[:index]
        newformat += str(nr)
        newformat += cls.format[index+1:]
        cls.format = newformat


class Time:

    starttime = time.time()
    times = [
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
    ]

    @classmethod
    def date(cls, daystr):
        "date from string."
        daystr = daystr.encode('utf-8', 'replace').decode("utf-8")
        for fmat in cls.times:
            try:
                return time.mktime(time.strptime(daystr, fmat))
            except ValueError:
                pass

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
                date = datetime.date.fromtimestamp(time.time())
                word = f"{date.year}-{date.month}-{date.day}" + " " + word
                res = cls.date(word.strip())
            if res:
                break
        return res

    @classmethod
    def timed(cls, datestr):
        "return time from string."
        if not datestr:
            return time.time()
        tme = cls.date(datestr)
        if not tme:
            tme = time.time()
        return tme

    @classmethod
    def today(cls):
        "start of the day."
        return str(datetime.datetime.today()).split()[0]


class Utils:

    @staticmethod
    def cdata(line):
        "scrape CDATA block."
        if "CDATA" in line:
            lne = line.replace("![CDATA[", "")
            lne = lne.replace("]]", "")
            lne = lne[1:-1]
            return lne
        return line

    @classmethod
    def cdir(cls, path):
        "create directory."
        if os.path.exists(path):
            return
        pth = pathlib.Path(path)
        if not os.path.exists(pth.parent):
            pth.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def clsname(obj):
        "return classname of an object."
        return obj.__class__.__name__

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
    def skip(obj):
        "skip underscored keys."
        result = []
        for x in dir(obj):
            if x.startswith("_"):
                continue
            result.append(x)
        return sorted(result)

    @staticmethod
    def skipped(obj):
        "yield values without underscored keys."
        for key in dir(obj):
            if key.startswith("_"):
                continue
            yield getattr(obj, key)

    @staticmethod
    def source(module):
        "return the source of a module."
        return module.__loader__.get_source(module.__name__)

    @staticmethod
    def spl(txt, ignore=""):
        "list from comma seperated string."
        try:
            ignores = ignore.split(",")
            result = txt.split(",")
        except (TypeError, ValueError):
            result = []
        return [x for x in result if x and x not in ignores]

    @staticmethod
    def strip(path, nr=3):
        "strip filename from path."
        return os.path.join(*path.split(os.sep)[-nr:])

    @staticmethod
    def striphtml(text):
        "strip html."
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text)

    @staticmethod
    def unescape(text):
        "unescape html."
        txt = re.sub(r"\s+", " ", text)
        return html.unescape(txt)

    @staticmethod
    def unquote(url):
        "unquote an url."
        return urllib.parse.unquote(url, errors='ignore')

    @staticmethod
    def useragent(txt):
        "produce useragent string."
        return "Mozilla/5.0 (X11; Linux x86_64) " + txt

    @staticmethod
    def where(obj):
        "path where object is defined."
        return os.path.dirname(inspect.getfile(obj))


def __dir__():
    return (
        'Logging',
        'Time',
        'Utils'
    )
