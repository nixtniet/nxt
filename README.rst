**NAME**


::

    NIXT - write your own commands


**SYNOPSIS**


::

    nixt <cmd> [-option] [--option] [arg=val] [arg==val] [arg-=val]


**INSTALL**


::

    due to lost access to my pypi account, use the latest from github

        $ git clone https://github.com/nixtniet/nixt
        $ cd nixt
        $ pipx install . --force


**DESCRIPTION**


::

    NIXT has it's modules in the ~/.nixt/mods directory so for a
    hello world command you would edit a file in ~/.nixt/mods/hello.py
    and add the following:


        def hello(event):
            event.reply("hello world !!")


    typing the hello command would result into a hello world !!:


        $ nixt hello
        hello world !!


**FILES**

::

    ~/.nixt
    ~/.local/bin/nixt
    ~/.local/share/pipx/venvs/nixt/*


**AUTHOR**


::

    Nixt Niet <nixtniet@gmail.com>


**COPYRIGHT**

::

    NIXT is Public Domain.
