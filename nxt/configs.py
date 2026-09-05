# This file is placed in the Public Domain.


"one config to rule them all"


class Helper:

    @classmethod
    def pkgname(cls, obj):
        "return package name of an object."
        return obj.__module__.split(".", maxsplit=1)[0]

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


class Config(type):

    def __getattr__(cls, key):
        if key in dir(cls):
            return cls.__getattribute__(cls, key)
        return ""

    def __str__(cls):
        return str(Helper.skip(cls.__dict__))


class Main(metaclass=Config):

    name = Helper.pkgname(Config)


def __dir__():
    return (
        'Config',
        'Main'
    )
