# Thsis file is placed in the Public Domain.


"help"


from nixt.defines import Main


TXT = """usage: %s [options] [cmd] [key=val] [key==val] [key-=val] [arguments]

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

use "%s cmd" for a list of commands.
"""

def hlp(msg):
    "show help."
    msg.reply(TXT % (
        Main.name,
        Main.name.upper(),
        Main.name
       )
    )
