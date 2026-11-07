# This file is placed in the Public Domain.


"program your own commands"


import inspect


from .clients import Clients
from .message import Message
from .methods import Dict
from .package import Mods
from .utility import Utils


class Commands:

    "command dispatch"

    cmds = {}
    names = {}

    @classmethod
    def add(cls, *funcs):
        "register a command."
        for func in funcs:
            name = Utils.funcname(func)
            cls.cmds[name] = func

    @classmethod
    def cmd(cls, txt):
        "parse single line to command and run it."
        msg = Message()
        msg.text = txt
        msg.kind = "command"
        cls.command(msg)
        return msg.result

    @classmethod
    def command(cls, msg):
        "command callback."
        Parser.parse(vars(msg), msg.text)
        func = cls.cmds.get(msg.cmd, cls.ondemand(msg.cmd))
        if func:
            func(msg)
            Clients.display(msg)
        msg.ready()

    @classmethod
    def list(cls):
        "scan for a list of all commands."
        result = []
        for modname in Mods.list():
            mod = Mods.get(modname)
            if not mod:
                continue
            result.extend([Utils.funcname(x) for x in cls.scan(mod, True)])
        return result

    @classmethod
    def ondemand(cls, name):
        "ondemand loading of commands."
        modname = cls.names.get(name, None)
        if not modname:
            return None
        mod = Mods.get(modname)
        if not mod:
            return None
        cls.scan(mod)
        return cls.cmds.get(name, None)

    @classmethod
    def scan(cls, mod, skip=False):
        "scan module for commands."
        result = []
        for nme, func in inspect.getmembers(mod, inspect.isfunction):
            if "cb_" in nme:
                continue
            if 'msg' in inspect.signature(func).parameters:
                if not skip:
                    cls.add(func)
                result.append(func)
        return result

    @classmethod
    def scanner(cls):
        "scan all modules."
        for name in Mods.list():
            mod = Mods.get(name)
            if not mod:
                continue
            cls.scan(mod)

    @classmethod
    def statics(cls):
        "read table."
        try:
            from .statics import NAMES
            cls.names.update(NAMES)
        except (ImportError, SyntaxError, ValueError):
            pass

    @classmethod
    def table(cls):
        "read static tables."
        cls.statics()
        if not cls.names:
            cls.scanner()


cmd = Commands.cmd


class Parser:

    "parsing for commands"

    @classmethod
    def init(cls, dct, text, clean=False):
        "set default values."
        data = {
            "args": [],
            "cmd": "",
            "gets": {},
            "index": None,
            "init": "",
            "mod": "",
            "opts": "",
            "otxt": text,
            "rest": "",
            "silent": {},
            "sets": {},
            "text": text
        }
        for k, v in data.items():
            if not clean:
                dct[k] = data.get(k, v) or v
            else:
                dct[k] = v

    @classmethod
    def parse(cls, dct, text, clean=False):
        "parse text for command and arguments."
        cls.init(dct, text, clean)
        args = []
        nr = -1
        for spli in text.split():
            if spli.startswith("--"):
                dct["opts"] += f",{spli[2:]}"
                continue
            if spli.startswith("-"):
                try:
                    dct["index"] = int(spli[1:])
                except ValueError:
                    dct["opts"] += spli[1:]
                continue
            if "-=" in spli:
                key, value = spli.split("-=", maxsplit=1)
                Dict.typed(dct["silent"], key, value)
                Dict.typed(dct["gets"], key, value)
                continue
            if "==" in spli:
                key, value = spli.split("==", maxsplit=1)
                Dict.typed(dct["gets"], key, value)
                continue
            if "=" in spli:
                key, value = spli.split("=", maxsplit=1)
                Dict.typed(dct["sets"], key, value)
                continue
            nr += 1
            if nr == 0:
                dct["cmd"] = spli
                continue
            args.append(spli)
        if args:
            dct["args"] = args
            dct["rest"] = " ".join(dct.get("args", []))
            dct["text"] = dct["cmd"] + " " + dct["rest"]
        if "v" in dct["opts"]:
            dct["verbose"] = True
        if "t" in dct["opts"]:
            dct["threaded"] = True


def __dir__():
    return (
        'Commands',
        'Parser',
        'cmd'
    )
