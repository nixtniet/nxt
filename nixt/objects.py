# This file is placed in the Public Domain.


"a clean namespace"


class Object:

    "inheritence without the methods"

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

    "defaulting to string"

    def __getattr__(self, key):
        if key in dir(self):
            return self.__getattribute__(key)
        return ""


def __dir__():
    return (
        'Data',
        'Object'
    )
