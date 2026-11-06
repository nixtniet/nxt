# This file is placed in the Public Domain.


"create systemd service file"


from nixt.defines import Main


def srv(msg):
    "generate systemd service file."
    if not Main.admin:
        return
    import getpass
    name = getpass.getuser()
    msg.reply(SYSTEMD % (
                           Main.name.upper(),
                           name,
                           name,
                           name,
                           Main.name
                          ))


SYSTEMD = """[Unit]
Description=%s
After=multi-user.target

[Service]
Type=simple
User=%s
Group=%s
ExecStart=/home/%s/.local/bin/%s -s

[Install]
WantedBy=multi-user.target"""
