# This file is placed in the Public Domain.


"find objects."


import time


from nixt.defines import Locater, Method, Time, Workdir


def fnd(msg):
    "find objects."
    if not msg.rest:
        res = sorted([x.split('.')[-1].lower() for x in Workdir.kinds()])
        if res:
            msg.reply(",".join(res))
        else:
            msg.reply("no data.")
        return
    otype = msg.args[0]
    nmr = 0
    for fnm, obj in sorted(
                           Locater.find(otype, msg.gets),
                           key=lambda x: Locater.fntime(x[0])
                          ):
        diff = time.time()-Locater.fntime(fnm)
        msg.reply(f"{nmr} {Method.fmt(obj)} {Time.elapsed(diff)}")
        nmr += 1
    if not nmr:
        msg.reply("no result")
