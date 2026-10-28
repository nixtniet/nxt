# This file is placed in the Public Domain.


"encoder/decoder"


import json
import types


from .default import RLock
from .typings import MappingProxyType


class Encoder(json.JSONEncoder):

    "object to string"

    lock = RLock()

    def default(self, o):
        "generate serializable versions."
        with Encoder.lock:
            if isinstance(o, type):
                return self.skip(o)
            if isinstance(o, dict):
                return o.items()
            if isinstance(o, list):
                return iter(o)
            if isinstance(o, MappingProxyType):
                return dict(o)
            try:
                return json.JSONEncoder.default(self, o)
            except TypeError:
                try:
                    return self.skip(o)
                except TypeError:
                    return repr(o)

    def skip(self, obj):
        "yield values without underscored keys."
        result = {}
        for key in dir(obj):
            if key.startswith("_"):
                continue
            value = getattr(obj, key, None)
            if isinstance(value, types.MethodType):
                continue
            result[key] = value
        return result


class JSON:

    "json wrapper"

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

    "line oriented"

    @classmethod
    def read(cls, fp, *args, **kw):
        "read from file."
        return cls.load(fp, *args, **kw)

    @classmethod
    def write(cls, obj, fp, *args, **kw):
        "dump object to disk."
        kw["indent"] = None
        kw["skipkeys"] = True
        kw["sort_keys"] = True
        cls.dump(obj, fp, *args, **kw)
        fp.write("\n")
        fp.flush()


def __dir__():
    return (
        'JSON',
        'JSONL'
    )
