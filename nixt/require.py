# This file is placed in the Public Domain.


"essential commands"


import inspect
import os


from .defines import JSON, MD5, Commands, Main, Mods, Utils, Worker


class Cmd:

    "necessary commands"

    @staticmethod
    def cmd(msg):
        "show commands."
        check = len(Commands.cmds) > len(Commands.names)
        msg.reply(",".join(sorted((check and Commands.cmds) or Commands.names)))

    @staticmethod
    def srv(msg):
        "generate systemd service file."
        import getpass
        name = getpass.getuser()
        msg.reply(SYSTEMD % (
            Main.name.upper(),
            name,
            name,
            name,
            Main.name
        ))

    @staticmethod
    def tbl(msg):
        "create table."
        core = {}
        md5s = {}
        Commands.names = {}
        if Main.mods:
            for name in Utils.spl(Main.mods):
                module = Mods.get(name, True)
                if not module:
                    continue
                if not module.__file__:
                    continue
                md5s[name] = MD5.md5(module.__file__)
                for cmd in Commands.scan(module):
                    Commands.names[Worker.getname(cmd)] = cmd.__module__.split(".")[-1]
        corepath = os.path.dirname(str(inspect.getsourcefile(Mods)))
        MD5.createmd5(corepath, core)
        msg.reply("# This file is placed in the Public Domain.")
        msg.reply("\n")
        msg.reply('"tables"')
        msg.reply("\n")
        msg.reply(f"CORE = {JSON.dumps(core, indent=4, sort_keys=True)}")
        msg.reply("\n")
        msg.reply(f"MODULES = {JSON.dumps(md5s, indent=4, sort_keys=True)}")
        msg.reply("\n")
        msg.reply(f"NAMES = {JSON.dumps(Commands.names, indent=4, sort_keys=True)}")
        msg.reply("\n")
        msg.reply("def __dir__():")
        msg.reply("    return (")
        msg.reply("        'CORE',")
        msg.reply("        'MODULES',")
        msg.reply("        'NAMES'")
        msg.reply("    )")

    @staticmethod
    def ver(msg):
        "show verson."
        msg.reply(f"{Main.name.upper()} {MD5.core()}")


SYSTEMD = """[Unit]
Description=%s
After=multi-user.target

[Service]
Type=simple
User=%s
Group=%s
ExecStart=/home/%s/.local/bin/%s -s

[Install]
WantedBy=multi-user.target"""


def __dir__():
    return (
        'Cmd',
    )
