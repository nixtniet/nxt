# This file is placed in the Public Domain.


"module management"


import os


from .default import Log
from .methods import Method
from .utility import MD5, Utils


logger = Log(__name__)


class Mods:

    "modules"

    core = {}
    dirs = {}
    md5s = {}
    mods = {}

    @classmethod
    def dir(cls, pkgname, path):
        "add module/path."
        cls.dirs[pkgname] = path

    @classmethod
    def get(cls, name, force=False):
        "return module from cache or import module."
        for pkgname, path in cls.dirs.items():
            modname = f"{pkgname}.{name}"
            mod = cls.mods.get(modname, None)
            if mod:
                return mod
            fnm = os.path.join(path, name + ".py")
            if not os.path.exists(fnm):
                continue
            if not force and cls.md5s:
                md5 = MD5.md5(fnm)
                md5s = cls.md5s.get(name)
                if md5s and md5 != md5s:
                    logger.info("mismatch %s", name)
            return cls.importer(modname, fnm)
        return None

    @classmethod
    def has(cls, attr):
        "return comma seperated string of module names containing an attribute."
        result = []
        for modname in cls.list():
            mod = cls.get(modname)
            if not mod:
                continue
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
    def list(cls, skip=""):
        "comma seperated list of available modules."
        mods = []
        for name, path in cls.dirs.items():
            if name in skip:
                continue
            if not os.path.exists(path):
                continue
            mods.extend(Utils.listdir(path))
        return sorted(set(mods))

    @classmethod
    def moddir(cls, name="modules"):
        "return package modules path."
        return os.path.join(Method.where(Mods), name)

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
