# This file is placed in the Public Domain.


"message"


import unittest


from nixt.defines import JSON, Message


jsontxt = '''{"a": "b", "args": [], "cmd": "", "index": 0, "kind": "message", "orig": "", "rest": "", "result": [], "text": ""}'''


class MyMessage(Message):

    "stub"

    a = ""


class TestMessage(unittest.TestCase):

    "message unittests"

    def test_construct(self):
        "test message construction."
        msg = Message()
        self.assertTrue(type(msg), Message)

    def test_json(self):
        "test message json dump."
        msg = MyMessage()
        msg.a = "b"
        txt = JSON.dumps(msg)
        self.assertEqual(txt, jsontxt)

    def test_ready(self):
        "test flagging a message ready."
        msg = Message()
        msg.ready()
        self.assertTrue(msg._ready.is_set())

    def test_reply(self):
        "test replying to a message."
        msg = Message()
        msg.reply("test")
        self.assertTrue("test" in msg.result)

    def test_wait(self):
        "test waiting for a message to complete."
        msg = Message()
        msg.ready()
        msg.wait()
        self.assertTrue(msg._ready.is_set())
