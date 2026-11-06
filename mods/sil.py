# This file is placed in the Public Domain.


"silence"


from nixt.defines import Broker


def lou(msg):
    "disable silent mode."
    bot = Broker.get(msg.orig)
    if not bot:
        msg.reply("no bot in fleet.")
        return
    bot.silent = False
    msg.ok()


def sil(msg):
    "enable silent mode."
    bot = Broker.get(msg.orig)
    if not bot:
        msg.reply("no bot in fleet.")
        return
    bot.silent = True
    msg.ok()
