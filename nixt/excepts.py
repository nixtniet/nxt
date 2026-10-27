# This file is placed in the Public Domain.


"default exception handler"


import traceback
import _thread


from .default import Log
from .message import Message


logger = Log(__name__)


class Errors:

    "error management"

    errors = []

    @classmethod
    def format(cls, exc):
        "format an exception"
        return traceback.format_exception(type(exc), exc, exc.__traceback__)

    @classmethod
    def defer(cls, exc, *args):
        "add an exception"
        excp = exc.with_traceback(exc.__traceback__)
        if excp not in cls.errors:
            cls.errors.append(excp)
        if args and isinstance(args[0], Message):
            args[0].ready()

    @classmethod
    def throw(cls, exc, *args):
        "log the exception and interrupt main loop."
        logger.exception(exc)
        _thread.interrupt_main()


def __dir__():
    return (
        'Errors',
    )
