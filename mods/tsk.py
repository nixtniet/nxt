# This file is placed in the Public Domain.


"running tasks"


import threading
import time


from nixt.defines import Time


def tsk(msg):
    "list of running tasks."
    result = []
    for thread in sorted(threading.enumerate(), key=lambda x: x.name):
        if str(thread).startswith("<_"):
            continue
        if getattr(thread, "sleep", None):
            uptime = float(thread.sleep) - float(time.time() - float(thread.state["latest"]))
        elif getattr(thread, "starttime", None):
            uptime = time.time() - thread.starttime
        else:
            uptime = time.time() - Time.starttime
        result.append((uptime, thread.name))
    res = []
    for uptime, txt in sorted(result, key=lambda x: x[0]):
        lap = Time.elapsed(uptime)
        res.append(f"{txt}/{lap}")
    if res:
        msg.reply(" ".join(res))
    else:
        msg.reply("no threads")
