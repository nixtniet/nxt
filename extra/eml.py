# This file is placed in the Public Domain.


"mailbox"


import os
import time


from mailbox import Maildir, mbox


from nixt.defines import Data, Disk, Locater, Method, Time


class Email(Data):

    "email record"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text: str


def eml(msg):
    "search emails."
    nrs = -1
    args = ["From", "Subject"]
    args.extend(msg.args)
    if msg.gets:
        args.extend(Method.keys(msg.gets))
    for key in msg.silent:
        if key in args:
            args.remove(key)
    arguments = list(set(args))
    result = sorted(
                    Locater.find("email", msg.gets),
                    key=lambda x: Time.timed(x[1].Date)
                   )
    if msg.index not in ["", None]:
        obj = result[msg.index]
        if obj:
            obj = obj[-1]
            tme = getattr(obj, "Date", "")
            diff = time.time() - Time.timed(tme)
            txt = Method.fmt(obj, arguments, plain=True)
            msg.reply(f'{msg.index} {txt} {Time.elapsed(diff)}')
    else:
        for _fn, obj in result:
            nrs += 1
            tme = getattr(obj, "Date", "")
            diff = time.time() - Time.timed(tme)
            txt = Method.fmt(obj, arguments, plain=True)
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
            tmp = Data()
            Method.update(tmp, mail)
            obj = Email()
            Method.update(obj, tmp._headers) # pylint: disable=W0212
            for payload in mail.walk():
                if payload.get_content_type() == 'text/plain':
                    load =  payload.get_payload()
                    if isinstance(load, str):
                        obj.text += load
                    else:
                        for line in load:
                            obj.text += str(line)
            obj.text = obj.text.replace("\\n", "\n")
            Disk.write(obj)
            nrs += 1
        if nrs:
            msg.ok(nrs)
    except FileNotFoundError as ex:
        msg.reply(str(ex))
