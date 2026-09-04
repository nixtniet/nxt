# This file is placed in the Public Domain.


"required commands"


import inspect
import os


from .command import Commands
from .configs import Main
from .encoder import JSON
from .hashing import MD5
from .package import Mods


class Cmd:

    @staticmethod
    def cmd(event):
        "show commands."
        check = len(Commands.cmds) > len(Commands.names)
        event.reply(",".join(sorted((check and Commands.cmds) or Commands.names)))

    @staticmethod
    def tbl(event):
        "create table."
        core = {}
        md5s = {}
        Commands.names = {}
        for name in Mods.list():
            module = Mods.get(name, True)
            md5s[name] = MD5.md5(module.__file__)
            for cmd in Commands.scan(module):
                Commands.names[cmd.__name__] = cmd.__module__.split(".")[-1]
        corepath = os.path.dirname(inspect.getsourcefile(Mods))
        MD5.createmd5(corepath, core)
        event.reply("# This file is placed in the Public Domain.")
        event.reply("\n")
        event.reply('"tables"')
        event.reply("\n")
        event.reply(f"CORE = {JSON.dumps(core, indent=4, sort_keys=True)}")
        event.reply("\n")
        event.reply(f"MODULES = {JSON.dumps(md5s, indent=4, sort_keys=True)}")
        event.reply("\n")
        event.reply(f"NAMES = {JSON.dumps(Commands.names, indent=4, sort_keys=True)}")
        event.reply("\n")
        event.reply("def __dir__():")
        event.reply("    return (")
        event.reply("        'CORE',")
        event.reply("        'MODULES',")
        event.reply("        'NAMES'")
        event.reply("    )")

    @staticmethod
    def ver(event):
        "show verson."
        event.reply(f"{Main.name.upper()} {MD5.core()}")


def __dir__():
    return (
        'Cmd',
    )
