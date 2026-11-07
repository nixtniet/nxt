# This file is placed in the Public Domain.


"a function with an object as the first argument"


import inspect
import os.path


from .typings import MethodType


class Dict:

    "yeah"

    @classmethod
    def deleted(cls, dct):
        "check whether obj had deleted flag set."
        return "__deleted__" in dct and dct["__deleted__"]

    @classmethod
    def edit(
        cls,
        dct,
        setter=None,
        skip=False
        ):
        "update object with dict."
        if setter is None:
            setter = {}
        for key, val in setter.items():
            if skip and val == "":
                continue
            cls.typed(dct, key, val)

    @classmethod
    def fmt(
        cls,
        dct,
        args=None,
        skip= None,
        plain=False,
        empty=False
        ):
        "format object info printable string."
        if args is None:
            args = list(dct.keys())
        if args == []:
            args = [x for x in dct if not x.startswith("_")]
        if skip is None:
            skip = []
        txt = ""
        for key in args:
            if key.startswith("__"):
                continue
            if key in skip:
                continue
            value = dct.get(key, None)
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
                txt += f"{key}={Method.clz(value)}({value!s}) "
        if txt == "":
            txt = "{}"
        return txt.strip()

    @classmethod
    def isempty(cls, dct):
        "check if all keys heve empty value."
        return all(not dct.get(key) for key in dct)

    @classmethod
    def notset(cls, dct1, dct2):
        "only set if not set."
        for key, value in dct2.items():
            if dct1.get(key, False):
                continue
            if value:
                dct1[key] = value

    @classmethod
    def search(
        cls,
        dct,
        selector=None,
        matching=False
        ):
        "check whether object matches search criteria."
        if selector is None:
            return False
        res = False
        for key, value in selector.items():
            val = dct.get(key, None)
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
    def skip(cls, dct, char=None):
        "skip class keys containing chars."
        if char is None:
            char = "_"
        res = {}
        for key in dct:
            if char in key:
                continue
            value = dct.get(key, None)
            if not value:
                continue
            if isinstance(value, MethodType):
                continue
            res[key] = value
        return res

    @classmethod
    def typed(cls, dct, key, val):
        "assign proper types."
        if dct is None or not val:
            return
        if val in ["True", "true", True]:
            dct[key] = True
            return
        if val in ["False", "false", False]:
            dct[key] = False
            return
        try:
            dct[key] = int(val)
            return
        except ValueError:
            pass
        try:
            dct[key] = float(val)
            return
        except ValueError:
            pass
        dct[key] = val


class Method:

    "methods"

    @classmethod
    def clsname(cls, obj):
        "class name of an object."
        if "__self__" in dir(obj):
            return obj.__self__.__class__.__name__
        return obj.__class__.__name__

    @classmethod
    def clz(cls, obj):
        "return class name of an object."
        return cls.fqn(obj).split(".")[-1]

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
    def getname(cls, obj):
        "string of function/method."
        if inspect.ismethod(obj):
            return f"{cls.clsname(obj)}.{obj.__name__}"
        if inspect.isfunction(obj):
            return repr(obj).split()[1]
        return repr(obj)

    @classmethod
    def modname(cls, obj):
        "return package name of an object."
        return obj.__module__.split(".")[-1]

    @classmethod
    def pkgname(cls, obj):
        "return package name of an object."
        return obj.__module__.split(".", maxsplit=1)[0]

    @classmethod
    def todict(cls, obj):
        "convert object to dictionary."
        res = {}
        for key in dir(obj):
            if key.startswith("_"):
                continue
            res[key] = getattr(obj, key)
        return res

    @classmethod
    def typed(cls, obj, key, value):
        "set typed values on the object."
        try:
            obj = vars(obj)
        except TypeError:
            pass
        Dict.typed(obj, key, value)

    @classmethod
    def update(cls, obj, data):
        "update object with a dict."
        for key, value in data.items():
            setattr(obj, key, value)

    @classmethod
    def where(cls, obj):
        "path where object is defined."
        return os.path.dirname(inspect.getfile(obj))


def __dir__():
    return (
        'Dict',
        'Method'
    )
