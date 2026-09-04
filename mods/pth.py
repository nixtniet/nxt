# This file is placed in the Public Domain.


"show path to website"


import os


from nxt.defines import Main, Utils


a = os.path.abspath
e = os.path.exists
j = os.path.join


def pth(event):
    "create and show path to website."
    path = j(a(Main.docs), "index.html")
    if e(path):
        event.reply(f"file://{path}")
    else:
        event.reply("no index.html")
