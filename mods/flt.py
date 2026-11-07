# This file is placed in the Public Domain.


"locate objects"


from nixt.defines import Broker, Method


def flt(msg):
    "list of running clients."
    try:
        index = int(msg.args[0])
    except (IndexError, ValueError):
        index = None
    clts = list(Broker.objs("announce"))
    if not clts:
        msg.reply("no clients")
        return
    if index is None:
        msg.reply(' | '.join([Method.fqn(o).split(".")[-1] for o in clts]))
        return
    if index < len(clts):
        msg.reply(str(clts[index]))
    else:
        msg.reply("no matching client.")
