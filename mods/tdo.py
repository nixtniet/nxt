# This file is placed in the Public Domain.


"todo"


from nixt.defines import Disk, Locater, Object


class Todo(Object):

    "todo item"

    def __init__(self):
        super().__init__()
        self.txt = ''


def dne(msg):
    "mark todo as done."
    if not msg.args:
        msg.iface("<txt>")
        return
    selector = {'txt': msg.args[0]}
    nmr = 0
    for fnm, dct in Locater.find('todo', selector):
        dct["__deleted_"] = True
        Disk.write(dct, fnm)
        msg.ok()
        break
    if not nmr:
        msg.reply("nothing todo")


def tdo(msg):
    "add a todo."
    if not msg.rest:
        msg.iface("<txt>")
        return
    dct = {}
    dct["txt"] = msg.rest
    Disk.write(dct, Disk.ident(Todo))
    msg.ok()
