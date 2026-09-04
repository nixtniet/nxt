# This file is placed in the Public Domain.


"write your own commands"


import unittest


from nxt.defines import Commands, Engine, Message


def cmnd(event):
    event.reply("yo!")


class TestCommands(unittest.TestCase):

    def test_construct(self):
        cmds = Commands()
        self.assertEqual(type(cmds), Commands)

    def test_add(self):
        Commands.add(cmnd)
        self.assertTrue("cmnd" in Commands.cmds)

    def test_get(self):
        Commands.add(cmnd)
        self.assertTrue(Commands.cmds.get("cmnd"))

    def test_command(self):
        clt = Engine()
        Commands.add(cmnd)
        evt = Message()
        evt.text = "cmnd"
        evt.orig = repr(clt)
        Commands.command(evt)
        self.assertTrue("yo!" in evt.result)
