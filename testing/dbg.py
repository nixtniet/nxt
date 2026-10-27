# This file is placed in the Public Domain.


"debug"


class Test(Exception):

    "custom exception"


def dbg(message):
    "raise exception."
    raise Test("Test")
