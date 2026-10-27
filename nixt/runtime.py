# This file is placed in the Public Domain.


"runtime"


import sys
import time


from argparse import SUPPRESS, ArgumentParser, RawTextHelpFormatter


from .defines import MD5, Booting, Commands, Errors, Main
from .defines import Message, Method, Mods, Screen
from .require import Cmd


class Arguments:

    "comamnd line arguments"

    @classmethod
    def getargs(cls):
        "parse commandline arguments."
        Main.name = Main.name or Method.pkgname(Main)
        theparser = cls.getparser()
        group = theparser.add_mutually_exclusive_group()
        group.add_argument("-c", "--console", action="store_true", help="start a console.")
        group.add_argument("-d", "--daemon", action="store_true", help="run as background daemon.")
        group.add_argument("-s", "--service", action="store_true", help="run as service.")
        parser = theparser.add_argument_group()
        parser.add_argument("-a", "--all", action="store_true", help="load all modules.")
        parser.add_argument("-l", "--level", default="info", help='set loglevel.', metavar="level")
        parser.add_argument("-v", "--verbose", action='store_true', help='enable verbose.')
        parser.add_argument("-w", "--wait", action='store_true', help='wait for services to start.')
        optionparser = theparser.add_argument_group()
        optionparser.add_argument("-m", "--mods", default="", help='modules to load.', metavar="m1,m2")
        optionparser.add_argument("-p", "--path", default='', help='path to modules directory.', metavar="path")
        optparser = theparser.add_argument_group()
        optparser.add_argument("--admin", action="store_true", help="enable admin mode.")
        optparser.add_argument("--channel", default="", help=SUPPRESS)
        optparser.add_argument("--nochdir", action="store_true", help=SUPPRESS)
        optparser.add_argument("--scanner", action="store_true", help="do full modules scan on boot.")
        optparser.add_argument("--wdr", default="", help="set modules directory.")
        args, arguments = theparser.parse_known_args()
        Method.updatecls(Main, vars(args))
        Main.otxt = " ".join(arguments)

    @classmethod
    def getparser(cls):
        "create parser."
        return ArgumentParser(
            prog=Main.name,
            description=f'{Main.name.upper()}',
            epilog='use "%(prog)s cmd" for a list of commands.',
            formatter_class=RawTextHelpFormatter,
            usage="%(prog)s [options] [cmd] [key=val] [key==val] [key-=val] [arguments]"
        )


class Kernel(Booting):

    "at first"

    @classmethod
    def banner(cls, force=False):
        "hello."
        if not force and not Main.verbose:
            return
        tmr = time.ctime(time.time()).replace("  ", " ")
        print(f"{Main.name.upper()} {tmr} {Main.level.upper() or 'INFO'} ({MD5.core()})")
        sys.stdout.flush()

    @classmethod
    def boot(cls):
        "configure runtime."
        cls.configure()
        if Main.all:
            Main.mods = ",".join(Mods.list())
        if Main.verbose:
            cls.banner()
        Commands.table()
        Mods.table()
        if Main.scanner or Main.local:
            Commands.scanner()

    @classmethod
    def errors(cls):
        "print errors."
        for error in Errors.errors:
            print("\n")
            for line in Errors.format(error):
                print(line.rstrip())


class CLI(Screen):

    "Command Line Interface"

    def __init__(self):
        Screen.__init__(self)
        self.register("command", Commands.command)

    def after(self, msg):
        "wait for msg to finish."
        msg.wait()

    def raw(self, text):
        "write to console."
        print(text.encode('utf-8', 'replace').decode("utf-8"))
        sys.stdout.flush()


class Console(CLI):

    "prompt"

    def __init__(self):
        CLI.__init__(self)
        self.silent = True

    def poll(self):
        "return msg."
        msg = Message()
        msg.orig = repr(self)
        msg.text = input("> ")
        msg.kind = "command"
        self.put(msg)
        return msg


class Scripts:

    "actual runtime"

    @staticmethod
    def background():
        "background script."
        Kernel.boot()
        Kernel.daemon()
        Kernel.privileges()
        Kernel.pid()
        Main.mods = ",".join(Mods.list())
        Kernel.init(Main.mods)
        Kernel.forever()

    @staticmethod
    def console():
        "console script."
        import readline
        readline.redisplay()
        Kernel.boot()
        Commands.add(Cmd.cmd)
        Kernel.init(Main.mods, Main.wait)
        csl = Console()
        csl.start()
        Kernel.forever()

    @staticmethod
    def control():
        "cli script."
        Kernel.boot()
        Commands.add(Cmd.cmd)
        if Main.admin:
            Commands.add(Cmd.tbl, Cmd.srv)
        cli = CLI()
        msg = Message()
        msg.kind = "command"
        msg.orig = repr(cli)
        msg.text = Main.otxt
        Commands.command(msg)
        msg.wait()

    @staticmethod
    def service():
        "service script."
        Kernel.boot()
        Kernel.privileges()
        Kernel.pid()
        if not Main.verbose:
            Kernel.banner(True)
        Main.mods = ",".join(Mods.list())
        Kernel.init(Main.mods)
        Kernel.forever()


def main():
    "dispatch to runtime."
    Arguments.getargs()
    if Main.console:
        Kernel.wrap(Scripts.console)
    elif Main.service:
        Kernel.wrap(Scripts.service)
    elif Main.daemon:
        Kernel.wrap(Scripts.background)
    else:
        Kernel.wrap(Scripts.control)


# if __name__ == "__main__":
#    main()
