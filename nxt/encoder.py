# This file is placed in the Public Domain.


"encoder/decoder"


import json
import threading
import types


class Encoder(json.JSONEncoder):

    lock = threading.RLock()

    def default(self, o):
        "generate serializable versions."
        with Encoder.lock:
            if isinstance(o, type):
                return self.skip(o)
            if isinstance(o, dict):
                return o.items()
            if isinstance(o, list):
                return iter(o)
            if isinstance(o, types.MappingProxyType):
                return dict(o)
            try:
                return json.JSONEncoder.default(self, o)
            except TypeError:
                try:
                    return vars(o)
                except TypeError:
                    return repr(o)

    def skip(self, obj):
        "yield values without underscored keys."
        o = {}
        for key in dir(obj):
            if key.startswith("_"):
                continue
            o[key] = getattr(obj, key)
        return o


class JSON:

    @classmethod
    def dump(cls, *args, **kw):
        "dump object to disk."
        kw["cls"] = Encoder
        return json.dump(*args, **kw)

    @classmethod
    def dumps(cls, *args, **kw):
        "dump object to string."
        kw["cls"] = Encoder
        return json.dumps(*args, **kw)

    @classmethod
    def load(cls, s, *args, **kw):
        "load object from disk."
        return json.load(s, *args, **kw)

    @classmethod
    def loads(cls, s, *args, **kw):
        "load object from string."
        return json.loads(s, *args, **kw)


class JSONL(JSON):

    @classmethod
    def log(cls, *args, **kw):
        "dump object to disk."
        kw["indent"] = None
        JSON.dump(cls, *args, **kw)

    @classmethod
    def logtxt(cls, *args, **kw):
        "dump object to string."
        kw["indent"] = None
        return JSON.dumps(*args, **kw)


def __dir__():
    return (
        'JSON',
        'JSONL'
    )
