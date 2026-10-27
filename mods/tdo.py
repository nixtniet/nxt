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
    for fnm, obj in Locater.find('todo', selector):
        nmr += 1
        obj.__deleted__ = True
        Disk.write(obj, fnm)
        msg.ok()
        break
    if not nmr:
        msg.reply("nothing todo")


def tdo(msg):
    "add a todo."
    if not msg.rest:
        msg.iface("<txt>")
        return
    obj = Todo()
    obj.txt = msg.rest
    Disk.write(obj)
    msg.ok()
