# This file is placed in the Public Domain.


"""**NAME**

::

    %s - %s


**SYNOPSIS**

::

    %s [options] [cmd] [key=val] [key==val] [key-=val] [arguments]


**DESCRIPTION**


::

    %s has all you need to program a unix cli program, such as disk
    perisistence for configuration files, msg handler to handle the
    client/server connection, bork on exit for have an early exit, etc.

    %s contains python3 code to program objects in a functional way.
    it provides an "clean namespace" Method class that only has dunder
    objects, so the namespace is not cluttered with method names. This
    makes storing and reading to/from json possible.

    %s is a python3 IRC bot, it can connect to IRC, fetch and
    display RSS feeds, take todo notes, keep a shopping list and log
    text. You can run it under systemd for 24/7 presence in a IRC channel.

    %s is Public Domain.


**INSTALL**

::

    $ pipx install %s
    $ pipx ensurepath

    <new terminal>

    $ %s --admin srv > %s.service
    $ sudo mv %s.service /etc/systemd/system/
    $ sudo systemctl enable %s --now

    joins ``#%s`` on localhost


**USAGE**

::

    $ %s -h

    usage: %s [options] [cmd] [key=val] [key==val] [key-=val] [arguments]

    %s

    options:
      -h, --help         show this help message and exit
      -c, --console      start a console.
      -d, --daemon       run as background daemon.
      -s, --service      run as service.

      -a, --all          load all modules.
      -l, --level level  set loglevel.
      -v, --verbose      enable verbose.
      -w, --wait         wait for services to start.

      -m, --mods m1,m2   modules to load.
      -p, --path path    path to modules directory.

      --admin            enable admin mode.
      --scanner          do full modules scan on boot.
      --wdr WDR          set modules directory.

    use "nixt cmd" for a list of commands.


**COMMANDS**

::

    atr - show attributes
    cfg - irc configuration
    cmd - commands
    dis - show deaths by disease
    dne - flag a todo as done
    dpl - sets display items
    eml - show emails
    err - show errors
    exp - export opml (stdout)
    fie - show fields of an object
    flt - show bots in fleet
    fnd - locate objects
    imp - import opml
    log - log text
    lou - enable loud mode
    man - create manual page
    mbx - import mailbox
    mod - show available modules
    nme - set name of a feed
    now - show genocide stats of today
    pth - show path to website on disk
    pwd - sasl nickserv name/pass
    rem - removes a rss feed
    req - request to the prosecutor
    res - restore objects
    rss - add a feed
    sil - enable silent mode
    srv - create service file
    syn - sync rss feeds
    tbl - create table module
    tdo - add todo item
    tsk - show running tasks
    tmr - timers
    udp - send udp packet to udp/irc relay
    upt - show uptime
    ver - version
    wdr - show working directory
    wsd - show wisdom


**CONFIGURATION**

::

    irc

    $ %s cfg irc server=<server>
    $ %s cfg irc hannel=<channel>
    $ %s cfg irc nick=<nick>

    sasl

    $ %s pwd <nsnick> <nspass>
    $ %s cfg irc password=<frompwd>


    rss

    $ %s rss <url>
    $ %s dpl <url> <item1,item2>
    $ %s rem <url>
    $ %s nme <url> <name>

    opml

    $ %s exp
    $ %s imp <filename>


**PROGRAMMING**

::

    %s has it's user modules in the ~/.%s/mods directory, for a hello world
    command you would edit a file in ~/.%s/mods/hello.py and add the following

        def hello(msg):
            msg.reply("hello world !!")

    typing the hello command would result into a nice hello world !!

        $ %s hello
        hello world !!


    commands run in their own thread and the program borks on exit to enable a
    short debug cycle, output gets flushed on print so exceptions appear in the
    systemd logs. modules can contain your own written python3 code.


**FILES**

::

    ~/.%s
    ~/.local/bin/%s
   `~/.local/share/pipx/venvs/%s/*


**AUTHOR**

::

    %s <%s>


**COPYRIGHT**

::

    %s is Public Domain."""


def man(msg):
    "create manual."
    args = msg.args
    try:
        name, email, author = args[0], args[1], " ".join(args[2:])
    except (ValueError, IndexError):
        msg.iface("<name> <email> <author>")
        return
    msg.reply(__doc__ % (
        name,
        name.upper(),
        *(name,) * 1,
        *(name.upper(),) * 4,
        *(name,) * 8,
        name.upper(),
        *(name,) * 11,
        name.upper(),
        *(name,) * 6,
        author,
        email,
        name.upper()
    ))
