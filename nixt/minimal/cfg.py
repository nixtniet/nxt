# This file is placed in the Public Domain.


"configuration"


from nixt.defines import Disk, Main, Method, Mods


def cfg(msg):
    "configure modules."
    if not msg.args:
        mods = "main," + Mods.has('Config')
        if mods and mods[-1] == ",":
            mods = mods[:-1]
        msg.iface(f"<{mods}>")
        return
    name = msg.args[0]
    if name != "main":
        mod = Mods.get(name)
        if not mod:
            msg.reply(f"no {name} module found.")
            return
        config = getattr(mod, "Config", None)
        if not config:
            msg.reply(f"no {name} config found.")
            return
    else:
        config = Main
    if not msg.sets:
        msg.reply(
            Method.fmt(
                config,
                vars(config).keys(),
                skip=["word",]
            )
        )
        return
    Method.edit(config, msg.sets)
    Disk.write(vars(config), name, "config")
    msg.ok()
