# This file is placed in the Public Domain.


"show path to website"


import os


from nixt.defines import Main


a = os.path.abspath
e = os.path.exists
j = os.path.join


def pth(msg):
    "create and show path to website."
    path = j(a(Main.docs), "index.html")
    if e(path):
        msg.reply(f"file://{path}")
    else:
        msg.reply("no index.html")
