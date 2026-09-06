# This file is placed in the Public Domain.


"a clean namespace"


import inspect
import os
import threading
import types


class Object:

    def __contains__(self, key):
        return key in dir(self)

    def __delitem__(self, key):
        del self.__dict__[key]

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __str__(self):
        return str(self.__dict__)


class Data(Object):

    def __getattr__(self, key):
        if key in dir(self):
            return self.__getattribute__(self, key)
        return ""


class Message(Data):

    def __init__(self):
        super().__init__()
        self._ready = threading.Event()
        self._thr = None
        self.args = []
        self.index = 0
        self.kind = "message"
        self.result = []

    def iface(self, txt):
        "show interface."
        txt = f"{self.cmd} {txt}"
        self.reply(txt)

    def ok(self, txt=""):
        "print ok response."
        self.reply(f"ok {txt}".strip())

    def ready(self):
        "flag message as ready."
        self._ready.set()

    def reply(self, text):
        "add text to result."
        self.result.append(text)

    def wait(self, timeout=0.0):
        "wait for completion."
        self._ready.wait(timeout or None)
        if self._thr:
            self._thr.join(timeout or None)


class Method:

    @classmethod
    def clear(cls, obj):
        "remove all items from the object."
        obj.__dict__.clear()

    @classmethod
    def clz(cls, obj):
        "return class name of an object."
        return cls.fqn(obj).split(".")[-1]

    @classmethod
    def clsname(cls, obj):
        "return classname of an object."
        return obj.__class__.__name__

    @classmethod
    def construct(cls, obj, *args, **kwargs):
        "object contructor."
        if args:
            val = args[0]
            if isinstance(val, zip):
                cls.update(obj, dict(val))
            elif isinstance(val, dict):
                cls.update(obj, val)
            else:
                cls.update(obj, vars(val))
        if kwargs:
            cls.update(obj, kwargs)

    @classmethod
    def copy(cls, obj):
        "return shallow copy of the object."
        oobj = type(obj)()
        cls.update(oobj, obj.__dict__.copy())
        return oobj

    @classmethod
    def deleted(cls, obj):
        "check whether obj had deleted flag set."
        return "__deleted__" in dir(obj) and obj.__deleted__

    @classmethod
    def edit(cls, obj, setter={}, skip=False):
        "update object with dict."
        for key, val in cls.items(setter):
            if skip and val == "":
                continue
            cls.typed(obj, key, val)

    @classmethod
    def fmt(cls, obj, args=[], skip=[], plain=False, empty=False):
        "format object info printable string."
        if args == []:
            args = list(obj.__dict__.keys())
        if args == []:
            args = [x for x in dir(obj) if not x.startswith("_")]
        txt = ""
        for key in args:
            if key.startswith("__"):
                continue
            if key in skip:
                continue
            value = getattr(obj, key, None)
            if value is None:
                continue
            if not empty and value == "":
                continue
            if plain:
                txt += f"{value} "
            elif isinstance(value, (int, float, dict, bool, list)):
                txt += f"{key}={value} "
            elif isinstance(value, str):
                txt += f'{key}="{value}" '
            else:
                txt += f"{key}={cls.clz(value)}({str(value)}) "
        if txt == "":
            txt = "{}"
        return txt.strip()

    @classmethod
    def fqn(cls, obj):
        "full qualified name."
        if "__qualname__" in dir(obj):
            kin = obj.__qualname__
        else:
            kin = str(type(obj)).split()[-1][1:-2]
        if kin == "type":
            kin = f"{obj.__module__}.{obj.__name__}"
        return kin

    @classmethod
    def fromkeys(cls, obj, keyz, value=None):
        "create a new object with keys from iterable and values set to value."
        return obj.__dict__.fromkeys(keyz, value)

    @classmethod
    def get(cls, obj, key, default=None):
        "return value for key if key is in the object, otherwise return default."
        try:
            return obj.__dict__.get(key, default)
        except AttributeError:
            return obj.get(key, default)

    @classmethod
    def isempty(cls, obj):
        "check if all keys heve empty value."
        for key in cls.keys(obj):
            if cls.get(obj, key):
                return False
        return True

    @classmethod
    def items(cls, obj):
        "object's key,value pairs."
        if isinstance(obj, type):
            return [(x, getattr(obj, x)) for x in dir(obj) if not x.startswith("_")]
        if isinstance(obj, dict):
            return obj.items()
        if isinstance(obj, types.MappingProxyType):
            return obj.items()
        return obj.__dict__.items()

    @classmethod
    def keys(cls, obj):
        "object's keys."
        if isinstance(obj, dict):
            return obj.keys()
        if isinstance(obj, types.MappingProxyType):
            return obj.keys()
        return obj.__dict__.keys()

    @classmethod
    def merge(cls, obj, obj2):
        "skip emoty values."
        for key, value in cls.items(obj2):
            if not value and getattr(obj, key, False):
                continue
            setattr(obj, key, value)

    @classmethod
    def modname(cls, obj):
        "return package name of an object."
        return obj.__module__.split(".")[-1]

    @classmethod
    def notset(cls, obj, obj2):
        "only set if not set."
        for key, value in cls.items(obj2):
            if getattr(obj, key, False):
                continue
            if value:
                setattr(obj, key, value)

    @classmethod
    def pkgname(cls, obj):
        "return package name of an object."
        return obj.__module__.split(".", maxsplit=1)[0]

    @classmethod
    def pop(cls, obj, key, default=None):
        "remove key from object and return it's value. return default or KeyError."
        return obj.__dict__.pop(key, default)

    @classmethod
    def popitem(cls, obj):
        "remove and return (key, value) pair."
        return obj.__dict__.popitem()

    @classmethod
    def reduce(cls, obj):
        "return dict with values setted attributes."
        result = {}
        for key, value in cls.items(obj):
            if value:
                result[key] = value
        return result

    @classmethod
    def search(cls, obj, selector={}, matching=False):
        "check whether object matches search criteria."
        res = False
        for key, value in cls.items(selector):
            val = getattr(obj, key, None)
            if not val:
                res = False
                break
            if matching and value != val:
                res = False
                break
            if str(value).lower() not in str(val).lower():
                res = False
                break
            res = True
        return res

    @classmethod
    def skip(cls, obj, chars="_"):
        "skip class keys containing chars."
        res = Object()
        for key, value in cls.items(obj):
            if isinstance(value, types.MethodType):
                continue
            donext = False
            for char in chars:
                if char in key:
                    donext = True
            if donext:
                continue
            setattr(res, key, value)
        return res

    @classmethod
    def skipped(cls, obj):
        "yield values without underscored keys."
        for key in dir(obj):
            if key.startswith("_"):
                continue
            yield getattr(obj, key)

    @classmethod
    def typed(cls, obj, key, val):
        "assign proper types."
        if not val:
            return
        if val in ["True", "true", True]:
            return setattr(obj, key, True)
        if val in ["False", "false", False]:
            return setattr(obj, key, False)
        try:
            return setattr(obj, key, int(val))
        except ValueError:
            pass
        try:
            return setattr(obj, key, float(val))
        except ValueError:
            pass
        setattr(obj, key, val)

    @classmethod
    def update(cls, obj, data, empty=True):
        "update object,"
        if isinstance(obj, type):
            if isinstance(data, type):
                for key in dir(data):
                    if '_' in key:
                        continue
                    value = getattr(data, key, None)
                    if value:
                        setattr(obj, key, value)
            else:
                for key, value in Method.items(data):
                    setattr(obj, key, value)
        elif isinstance(obj, dict):
            if isinstance(data, dict):
                obj.update(data)
            else:
                obj.update(data.__dict__)
        elif isinstance(obj.__dict__, types.MappingProxyType):
            for key, value in data.items():
                setattr(obj, key, value)
        elif isinstance(data, dict):
            obj.__dict__.update(data)
        else:
            obj.__dict__.update(data.__dict__)

    @classmethod
    def values(cls, obj):
        "object's values."
        if isinstance(obj, type):
            return [getattr(obj, x) for x in dir(obj) if not x.startswith("_")]
        if isinstance(obj, dict):
            return obj.values()
        if isinstance(obj.__dict__, types.MappingProxyType):
            res = []
            for key in obj.__dict__:
                res.append(obj[key])
            return res
        return obj.__dict__.values()

    @classmethod
    def where(cls, obj):
        "path where object is defined."
        return os.path.dirname(inspect.getfile(obj))


class Parser:

    @classmethod
    def parse(cls, obj, text, clean=False):
        "parse text for command and arguments."
        data = {
            "args": [],
            "cmd": "",
            "gets": Data(),
            "index": None,
            "init": "",
            "mod": "",
            "opts": "",
            "otxt": text,
            "rest": "",
            "silent": Data(),
            "sets": Data(),
            "text": text
        }
        for k, v in data.items():
            if not clean:
                setattr(obj, k, getattr(obj, k, v) or v)
            else:
                setattr(obj, k, v)
        args = []
        nr = -1
        for spli in text.split():
            if spli.startswith("--"):
                name = spli[2:]
                setattr(obj, name, True)
                continue
            if spli.startswith("-"):
                try:
                    obj.index = int(spli[1:])
                except ValueError:
                    obj.opts += spli[1:]
                continue
            if "-=" in spli:
                key, value = spli.split("-=", maxsplit=1)
                Method.typed(obj.silent, key, value)
                Method.typed(obj.gets, key, value)
                continue
            if "==" in spli:
                key, value = spli.split("==", maxsplit=1)
                Method.typed(obj.gets, key, value)
                continue
            if "=" in spli:
                key, value = spli.split("=", maxsplit=1)
                Method.typed(obj.sets, key, value)
                continue
            nr += 1
            if nr == 0:
                obj.cmd = spli
                continue
            args.append(spli)
        if args:
            obj.args = args
            obj.text = obj.mod + " " + obj.cmd
            obj.rest = " ".join(obj.args)
            obj.text = obj.text + " " + obj.rest
        else:
            obj.text = obj.mod + " " + obj.cmd


def __dir__():
    return (
        'Data',
        'Message',
        'Method',
        'Object',
        'Parser'
    )
