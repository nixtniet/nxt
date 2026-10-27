# This file is placed in the Public Domain.


"show fields on an object"


from nixt.defines import Locater, Workdir


def fie(msg):
    "show fields of a type."
    if not msg.rest:
        res = sorted({x.split('.')[-1].lower() for x in Workdir.kinds()})
        if res:
            msg.reply(",".join(res))
        else:
            msg.reply("no types")
        return
    itms = Locater.attrs(msg.args[0])
    if not itms:
        msg.reply("no attributes")
    else:
        msg.reply(",".join(itms))
