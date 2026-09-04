# This file is placed in the Public Domain.


"module management"


import os


from .hashing import MD5
from .utility import Utils


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
            mods.extend(Utils.listdir(path))
        return sorted(set(mods))

    @classmethod
    def minimal(cls):
        "return package minimal path."
        return os.path.join(Utils.where(Mods), "minimal")

    @classmethod
    def moddir(cls):
        "return package modules path."
        return os.path.join(Utils.where(Mods), "modules")

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


def __dir__():
    return (
        'Mods',
    )
