# This file is placed in the Public Domain.


"find objects."


import time


from nxt.defines import Locater, Method, Time, Workdir


def fnd(event):
    "find objects."
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in Workdir.kinds()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no data.")
        return
    otype = event.args[0]
    nmr = 0
    for fnm, obj in sorted(
                           Locater.find(otype, event.gets),
                           key=lambda x: Locater.fntime(x[0])
                          ):
        diff = time.time()-Locater.fntime(fnm)
        event.reply(f"{nmr} {Method.fmt(obj)} {Time.elapsed(diff)}")
        nmr += 1
    if not nmr:
        event.reply("no result")
