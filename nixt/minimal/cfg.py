# This file is placed in the Public Domain.


"configuration"


from nixt.defines import Data, Disk, Method, Mods


def cfg(msg):
    "configure modules."
    if not msg.args:
        mods = "main," + Mods.has('Config')
        if mods and mods[-1] == ",":
            mods = mods[:-1]
        msg.iface(f"<{mods}>")
        return
    name = msg.args[0]
    config = Data()
    Disk.read(config, name, "config")
    if name != "main" and not config:
        mod = Mods.get(name)
        if not mod:
            msg.reply(f"no {name} module found.")
            return
        config = getattr(mod, "Config", None)
        if not config:
            msg.reply(f"no {name} config found.")
            return
    if not msg.sets:
        msg.reply(
            Method.fmt(
                config,
                Method.keys(config),
                skip=["word",]
            )
        )
        return
    Method.edit(config, msg.sets)
    Disk.write(config, name, "config")
    msg.ok()
