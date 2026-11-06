# This file is placed in the Public Domain.


"background daemon"


from .configs import Main
from .persist import Workdir


class Daemon:

    "detach from console"

    @classmethod
    def daemon(cls):
        "run in the background."
        import os
        import sys
        pid = os.fork()
        if pid != 0:
            os._exit(0)
        os.setsid()
        pid2 = os.fork()
        if pid2 != 0:
            os._exit(0)
        if not Main.verbose:
            cls.null(sys.stdin)
            cls.null(sys.stdout)
            cls.null(sys.stderr)
        os.umask(0o077)
        os.chdir("/")
        os.nice(10)

    @classmethod
    def null(cls, iostream):
        "route to /dev/null."
        import os
        with open('/dev/null', 'r', encoding="utf-8") as sis:
            os.dup2(sis.fileno(), iostream.fileno())

    @classmethod
    def pid(cls):
        "return pid path."
        return Workdir.pid(Main.name)

    @classmethod
    def privileges(cls):
        "drop privileges."
        import getpass
        import os
        import pwd
        pwnam2 = pwd.getpwnam(getpass.getuser())
        os.setgid(pwnam2.pw_gid)
        os.setuid(pwnam2.pw_uid)


def __dir__():
    return (
        'Daemon',
    )
