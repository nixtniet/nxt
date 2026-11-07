# This file is placed in the Public Domain.


"mailbox"


import os
import time


from mailbox import Maildir, mbox


from nixt.defines import Data, Dict, Disk, Locater, Time


class Email(Data):

    "email record"


def eml(msg):
    "search emails."
    nrs = -1
    args = ["From", "Subject"]
    args.extend(msg.args)
    if msg.gets:
        args.extend(msg.gets.keys())
    for key in msg.silent:
        if key in args:
            args.remove(key)
    arguments = list(set(args))
    result = sorted(
                    Locater.objects("email", msg.gets),
                    key=lambda x: Time.timed(x[1].Date)
                   )
    if msg.index not in ["", None]:
        dct = result[msg.index]
        if dct:
            tme = dct.get("Date", "")
            diff = time.time() - Time.timed(tme)
            txt = Dict.fmt(dct, arguments, plain=True)
            msg.reply(f'{msg.index} {txt} {Time.elapsed(diff)}')
    else:
        for dct in result:
            nrs += 1
            tme = dct.get("Date", "")
            diff = time.time() - Time.timed(tme)
            txt = Dict.fmt(dct, arguments, plain=True)
            msg.reply(f'{nrs} {txt} {Time.elapsed(diff)}')
    if not result:
        msg.reply("no emails found.")


def mbx(msg):
    "import emails from mailbox."
    if not msg.args:
        msg.iface("<path>")
        return
    fnm = os.path.expanduser(msg.args[0])
    if not os.path.exists(fnm):
        msg.iface("<path>")
        return
    msg.reply(f"reading from {fnm}")
    if os.path.isdir(fnm):
        thing = Maildir(fnm, create=False)
    elif os.path.isfile(fnm):
        thing = mbox(fnm, create=False)
    else:
        return
    try:
        thing.lock()
    except FileNotFoundError:
        pass
    nrs = 0
    try:
        for mail in thing:
            dct = {}
            dct.update(mail)
            dct.update(mail.get("_headers", {}))
            for payload in mail.walk():
                if payload.get_content_type() == 'text/plain':
                    load =  payload.get_payload()
                    if isinstance(load, str):
                        dct["text"] += load
                    else:
                        for line in load:
                            dct["text"] += str(line)
            dct["text"] = dct["text"].replace("\\n", "\n")
            Disk.write(dct, Disk.ident(Email))
            nrs += 1
        if nrs:
            msg.ok(nrs)
    except FileNotFoundError as ex:
        msg.reply(str(ex))
