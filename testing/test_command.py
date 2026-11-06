# This file is placed in the Public Domain.


"write your own commands"


import unittest


from nixt.defines import Commands, Handler, Message


def cmnd(msg):
    "test command."
    msg.reply("yo!")


class TestCommands(unittest.TestCase):

    "commands unittests"

    def test_construct(self):
        "test commands construction."
        cmds = Commands()
        self.assertEqual(type(cmds), Commands)

    def test_add(self):
        "test adding a command."
        Commands.add(cmnd)
        self.assertTrue("cmnd" in Commands.cmds)

    def test_get(self):
        "test getting a command."
        Commands.add(cmnd)
        self.assertTrue(Commands.cmds.get("cmnd"))

    def test_command(self):
        "test running a command."
        clt = Handler()
        Commands.add(cmnd)
        msg = Message()
        msg.text = "cmnd"
        msg.orig = repr(clt)
        Commands.command(msg)
        self.assertTrue("yo!" in msg.result)
