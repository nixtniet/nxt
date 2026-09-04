# This file is placed in the Public Domain.


"engine"


import unittest


from nxt.defines import Client, Engine, Message


buffer = []


def hello(event):
    event.reply(event.text)
    event.ready()


class MyClient(Client, Engine):

    def __init__(self):
        Engine.__init__(self)
        Client.__init__(self)
        self.register("hello", hello)

    def raw(self, text):
        buffer.append(text)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.clt = MyClient()
        self.clt.silent = False
        self.clt.start()

    def shutDown(self):
        self.clt.stop()

    def test_announce(self):
        self.clt.announce("hello")
        self.assertTrue("hello" in buffer)

    def test_display(self):
        evt = Message()
        evt.reply("test1")
        evt.reply("test2")
        self.clt.display(evt)
        self.assertTrue("test1" in buffer)
        self.assertTrue("test2" in buffer)
        self.assertTrue(buffer.index("test1") < buffer.index("test2"))

    def test_dosay(self):
        self.clt.dosay("#channel", "yo!")
        self.assertTrue("yo!" in buffer)

    def test_put(self):
        evt = Message()
        evt.kind = "hello"
        evt.text = "hi world"
        self.clt.put(evt)
        evt.wait()
        self.assertTrue("hi world" in evt.result)
