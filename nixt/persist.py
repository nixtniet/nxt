# This file is placed in the Public Domain.


"path to object cache"


import json
import os
import time


from datetime import datetime


from .encoder import JSON
from .objects import Dict
from .methods import Method
from .typings import MappingProxyType
from .utility import Log, Path, RLock, Utils


logger = Log(__name__)


class DecodeError(Exception):

    "could not parse to JSON"


class MissingPath(Exception):

    "don't know where to write"


class Cache:

    "path object cache"

    paths = {}

    @classmethod
    def add(cls, path, obj):
        "put object into cache."
        cls.paths[path] = obj

    @classmethod
    def get(cls, path):
        "get object from cache."
        return cls.paths.get(path, None)

    @classmethod
    def sync(cls, path, obj):
        "update cached object."
        if not isinstance(obj, (dict, MappingProxyType)):
            raise TypeError(type(obj))
        try:
            cls.paths[path].update(obj)
        except (KeyError, AttributeError):
            cls.add(path, obj)


class Disk:

    "read/write disk"

    lock = RLock()

    @classmethod
    def ident(cls, name):
        "return ident string for object."
        return os.path.join(name, *str(datetime.now(tz=None)).split())

    @classmethod
    def read(cls, path, base="store"):
        "read object from path."
        with cls.lock:
            pth = os.path.join(Workdir.wdr, base, path)
            logger.debug("read %s/%s", base, path)
            if not os.path.exists(pth):
                return {}
            with open(pth, "r", encoding="utf-8") as fpt:
                try:
                    return JSON.load(fpt)
                except json.JSONDecodeError as ex:
                    raise DecodeError(Utils.strip(pth)) from ex

    @classmethod
    def write(cls, obj, path=None, base="store"):
        "write object to disk."
        if not path:
            try:
                path = cls.ident(Method.fqn(obj))
            except TypeError:
                pass
        if not path:
            raise MissingPath
        try:
            obj = vars(obj)
        except TypeError:
            pass
        with cls.lock:
            pth = os.path.join(Workdir.wdr, base, path)
            logger.debug("write %s/%s", base, path)
            Utils.cdir(pth)
            with open(pth, "w", encoding="utf-8") as fpt:
                JSON.dump(obj, fpt, indent=4)
            Cache.sync(path, obj)
            return path


class Locater:

    "find objects"

    lock = RLock()

    @classmethod
    def attrs(cls, kind):
        "show attributes for kind of objects."
        result = []
        for _pth, obj in cls.find(kind, nritems=1):
            if not obj:
                continue
            result.extend(obj.keys())
        return set(result)

    @classmethod
    def count(cls, kind):
        "count kinds of objects."
        return len(list(cls.find(kind)))

    @classmethod
    def find(
        cls,
        kind,
        selector=None,
        removed=False,
        matching=False,
        nritems=0
        ):
        "locate objects by matching atributes."
        if selector is None:
            selector = {}
        try:
            selector = vars(selector)
        except TypeError:
            pass
        nrs = 0
        for pth in cls.fns(Workdir.long(kind)):
            obj = Cache.get(pth)
            if not obj:
                obj = Disk.read(pth)
                Cache.add(pth, obj)
            if not removed and Method.deleted(obj):
                continue
            if selector and not Method.search(obj, selector, matching):
                continue
            if nritems and nrs >= nritems:
                break
            nrs += 1
            yield (pth, obj)

    @classmethod
    def first(cls, obj, selector=None):
        "return first object of a kind."
        result = sorted(
                        cls.find(Method.fqn(obj), selector),
                        key=lambda x: cls.fntime(x[0])
                       )
        res = ""
        if result:
            inp = result[0]
            Dict.update(obj, inp[-1])
            res = inp[0]
        return res

    @classmethod
    def fns(cls, kind):
        "file names by kind of object."
        path = os.path.join(Workdir.wdr, "store", kind)
        for rootdir, dirs, _files in os.walk(path, topdown=True):
            for dname in dirs:
                if dname.count("-") != 2:
                    continue
                ddd = os.path.join(rootdir, dname)
                for fll in os.listdir(ddd):
                    yield cls.strip(os.path.join(ddd, fll))

    @classmethod
    def fntime(cls, daystr):
        "time from path."
        datestr = " ".join(daystr.split(os.sep)[-2:])
        datestr = datestr.replace("_", " ")
        if "." in datestr:
            datestr, rest = datestr.rsplit(".", 1)
        else:
            rest = ""
        timd = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
        if rest:
            try:
                timd += float("." + rest)
            except ValueError:
                pass
        return float(timd)

    @classmethod
    def last(cls, obj, selector=None):
        "last saved version."
        result = sorted(
            cls.find(Method.fqn(obj), selector),
            key=lambda x: cls.fntime(x[0])
        )
        res = ""
        if result:
            inp = result[-1]
            obj.update(inp[-1])
            res = inp[0]
        return res

    @classmethod
    def objects(
        cls,
        kind,
        selector=None,
        removed=False,
        matching=False,
        nritems=0
        ):
        "return objects by matching atributes."
        yield from [x[1] for x in cls.find(
            kind,
            selector,
            removed,
            matching,
            nritems
        )]

    @classmethod
    def strip(cls, path):
        "strip filename from path."
        return path.rsplit('store', maxsplit=1)[-1][1:]


class Stated:

    "state of wisdom"

    def __init__(self):
        super().__init__()
        self.fnm = ""

    def dump(self):
        "dump state to disk."
        if not self.fnm:
            self.fnm = Locater.first(self)
        Disk.write(self, self.fnm)

    def load(self):
        "load from disk."
        Locater.first(self)


class Workdir:

    "the store everything directory"

    wdr = ""

    @classmethod
    def home(cls, name):
        "return home working directory."
        return os.path.expanduser(f"~/.{name}")

    @classmethod
    def kinds(cls):
        "show kind on objects in cache."
        assert cls.wdr
        path = os.path.join(cls.wdr, "store")
        if not os.path.exists(path):
            cls.skel()
        return os.listdir(path)

    @classmethod
    def logdir(cls, path=""):
        "return directory to logs."
        assert cls.wdr
        return os.path.join(cls.wdr, "logs", path)

    @classmethod
    def long(cls, name):
        "expand to fqn."
        if "." in name:
            return name
        split = name.rsplit(".", maxsplit=1)[-1].lower()
        res = name
        for names in cls.kinds():
            if split == names.split(".")[-1].lower():
                res = names
                break
        return res

    @classmethod
    def moddir(cls):
        "return modules directory."
        assert cls.wdr
        return os.path.join(cls.wdr, "mods")

    @classmethod
    def pid(cls, name):
        "write pid to file."
        assert cls.wdr
        filename = os.path.join(cls.wdr, f"{name}.pid")
        if os.path.exists(filename):
            os.unlink(filename)
        path2 = Path(filename)
        path2.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as fds:
            fds.write(str(os.getpid()))

    @classmethod
    def skel(cls):
        "create directories."
        assert cls.wdr
        if not os.path.exists(cls.wdr):
            Utils.cdir(cls.wdr)
        path = os.path.abspath(cls.wdr)
        for wpth in ["config", "logs", "mods", "store"]:
            pth = Path(os.path.join(path, wpth))
            pth.mkdir(parents=True, exist_ok=True)


def __dir__():
    return (
        'Disk',
        'Locater',
        'Selector',
        'Stated',
        'Workdir'
    )
