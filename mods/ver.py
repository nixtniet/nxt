# This file is placed in the Public Domain.


"show version"


from nixt.defines import MD5
from nixt.defines import Main


def ver(msg):
    "show verson."
    msg.reply(f"{Main.name.upper()} {MD5.core()}")
