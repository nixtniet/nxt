# Thsis file is placed in the Public Domain.


"help"


from nxt.defines import Main


TXT = """usage: %s <cmd> [name=value] [name==value]

NIXT

options:
  -h, --help     show this help message and exit
  --console      run as console.
  --daemon       run as background daemon.
  --service      run as service.

  --admin        enable admin mode.
  --user         use local mods directory.

  --all          load all modules.
  --verbose      enable verbose.
  --wait         wait for services to start.

  level=level    set loglevel.
  mods=m1,m2     modules to load.
  path=path      path to working directory.

use "%s cmd" for a list of commands.
"""


def hlp(event):
    event.reply(TXT % (
        Main.name,
        Main.name
       )
    )
