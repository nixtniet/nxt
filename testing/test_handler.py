# This file is placed in the Public Domain.


"engine"


import unittest


from nixt.defines import Handler, Message


buffer = []


def hello(message):
    "demo function."
    message.reply(message.text)
    message.ready()


class TestHandler(unittest.TestCase):

    "unittest to test the callback engine"

    hdl = Handler()

    def setUp(self): # pylint: disable=C0103
        "setup engine."
        self.hdl.register("hello", hello)
        self.hdl.start()

    def shutDown(self): # pylint: disable=C0103
        "shutdown engine."
        self.hdl.stop()

    def test_callback(self):
        "test callback dispatching."
        msg = Message()
        msg.kind = "hello"
        msg.text = "hello"
        self.hdl.handle(msg)
        msg.wait()
        self.assertTrue("hello" in msg.result)

    def test_set(self):
        "test whether loop handles a message."
        msg = Message()
        msg.kind = "hello"
        msg.text = "hello"
        self.hdl.put(msg)
        msg.wait()
        self.assertTrue(msg._ready.is_set())

    def test_loop2(self):
        "test whether result is being set."    
        msg = Message()
        msg.kind = "hello"
        msg.text = "hello bot"
        self.hdl.put(msg)
        msg.wait()
        self.assertTrue("hello bot" in msg.result)

    def test_put(self):
        "test push/get from queue."
        hdl = Handler()
        msg = Message()
        msg.kind = "hello"
        hdl.put(msg)
        message = hdl.queue.get()
        self.assertTrue(message is msg)

    def test_register(self):
        "test callback register."
        self.hdl.register("hlo", hello)
        self.assertTrue(hello in self.hdl.cbs.values())

    def test_start(self):
        "test engine start."
        hdl = Handler()
        hdl.start()
        self.assertTrue(not hdl.stopped.is_set())

    def test_stop(self):
        "test engine stop."
        self.hdl.stop()
        self.assertTrue(self.hdl.stopped.is_set())
