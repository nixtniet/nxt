# This file is placed in the Public Domain.


"one config to rule them all"


from .methods import Method


class Config(type):

    "config meta class"

    def __getattr__(cls, key):
        if key in dir(cls):
            return cls.__getattribute__(key)
        return ""

    def __str__(cls):
        return str(Method.skip(dict(cls.__dict__)))


class Cfg(metaclass=Config):

    "inheritable config"


class Main(metaclass=Config):

    "main config"

    mods = ""
    name = Method.pkgname(Config)
    otxt = ""
    path = ""


def __dir__():
    return (
        'Cfg',
        'Config',
        'Main'
    )
