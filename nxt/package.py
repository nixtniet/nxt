# This file is placed in the Public Domain.


"module management"


import inspect
import os


class MisMatch(Exception):

    "md5 sums don't match."


class Mods:

    core = {}
    dirs = {}
    md5s = {}
    mods = {}

    @classmethod
    def dir(cls, pkgname, path=None):
        "add module/path."
        if not pkgname:
            return
        pkgn = pkgname
        if path is None:
            path = pkgname
            pkgn = ".".join(pkgname.split(os.sep)[-2:])
        cls.dirs[pkgn] = path

    @classmethod
    def get(cls, name, force=False):
        "return module from cache or import module."
        for pkgname, path in cls.dirs.items():
            modname = f"{pkgname}.{name}"
            try:
                mod = cls.mods.get(modname, None)
            except MisMatch:
                continue
            if mod:
                return mod
            fnm = os.path.join(path, name + ".py")
            if not os.path.exists(fnm):
                continue
            return cls.importer(modname, fnm)

    @classmethod
    def has(cls, attr):
        "return list of modules containing an attribute."
        result = []
        for modname in cls.list():
            mod = cls.get(modname)
            if not getattr(mod, attr, False):
                continue
            result.append(mod.__name__.split(".")[-1])
        return ",".join(result)

    @classmethod
    def importer(cls, name, pth=""):
        "import module by path."
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, pth)
        if not spec or not spec.loader:
            return None
        cls.mods[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mods[name])
        return cls.mods[name]

    @classmethod
    def list(cls):
        "comma seperated list of available modules."
        mods = []
        for pkgname, path in cls.dirs.items():
            if not os.path.exists(path):
                continue
            mods.extend(cls.listdir(path))
        return sorted(set(mods))

    @classmethod
    def listdir(cls, path, ignore=""):
        "list modules in a directory."
        return [
                x[:-3] for x in os.listdir(path)
                if x.endswith(".py") and
                not x.startswith("__") and
                x[:-3] not in cls.spl(ignore)
               ]

    @classmethod
    def minimal(cls):
        "return package minimal path."
        return os.path.join(cls.where(Mods), "minimal")

    @classmethod
    def moddir(cls):
        "return package modules path."
        return os.path.join(cls.where(Mods), "modules")

    @classmethod
    def source(module):
        "return the source of a module."
        return module.__loader__.get_source(module.__name__)

    @classmethod
    def spl(cls, txt, ignore=""):
        "list from comma seperated string."
        try:
            ignores = ignore.split(",")
            result = txt.split(",")
        except (TypeError, ValueError):
            result = []
        return [x for x in result if x and x not in ignores]

    @classmethod
    def statics(cls):
        "read table,"
        try:
            from .statics import CORE
            cls.core.update(CORE)
        except (ImportError, SyntaxError, ValueError):
            pass
        try:
            from .statics import MODULES
            cls.md5s.update(MODULES)
        except (ImportError, SyntaxError, ValueError):
            pass

    @classmethod
    def table(cls):
        "read static tables."
        cls.statics()
        if cls.core:
            MD5.check(cls.core)

    @classmethod
    def where(cls, obj):
        "path where object is defined."
        return os.path.dirname(inspect.getfile(obj))


class MD5:

    @classmethod
    def check(cls, md5s):
        "check for md5sums in a given path."
        ok = True
        path = os.path.dirname(__spec__.origin)
        if not os.path.exists(path):
            return False
        for pth in os.listdir(path):
            if pth.startswith("__") or not pth.endswith(".py") or "statics" in pth:
                continue
            name = pth[:-3]
            modpath = os.path.join(path, pth)
            if md5s and cls.md5(modpath) != md5s.get(name):
                ok = False
        return ok

    @classmethod
    def core(cls):
        "calculate md5 of the statics module."
        try:
            from . import statics
        except (ModuleNotFoundError, ImportError, SyntaxError):
            return ""
        return cls.source(Mods.source(statics))[:7].upper()

    @classmethod
    def createmd5(cls, path, data):
        for pth in os.listdir(path):
            if pth.startswith("__") or not pth.endswith(".py") or "statics" in pth:
                continue
            name = pth[:-3]
            data[name] = cls.md5(os.path.join(path, pth))

    @classmethod
    def dir(cls, path, md5):
        "create a md5 for a directory."
        for fnm in os.listdir(path):
            if not fnm.endswith(".py"):
                continue
            mpath = os.path.join(path, fnm)
            with open(mpath, "r", encoding="utf-8") as file:
                md5.update(file.read().encode("utf-8"))

    @classmethod
    def md5(cls, path):
        "calculate md5sum of a file."
        import hashlib
        md5 = hashlib.md5()
        with open(path, "r", encoding="utf-8") as file:
            md5.update(file.read().encode("utf-8"))
        return str(md5.hexdigest())

    @classmethod
    def source(cls, src):
        "determine md5 of source code."
        import hashlib
        md5 = hashlib.md5()
        md5.update(src.encode("utf-8"))
        return str(md5.hexdigest())



def __dir__():
    return (
        'MD5',
        'Mods'
    )
