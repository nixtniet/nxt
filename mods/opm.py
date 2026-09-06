# This file is placed in the Public Domain.


"Outline Processor Markup Language"


import os
import urllib
import _thread


from nxt.defines import Disk, Locater, Method, Utils


from .rss import Rss


class Locks:

    importlock = _thread.allocate_lock()


class OPML:

    @classmethod
    def getnames(cls, line):
        "get names from line."
        return [x.split('="')[0] for x in line.split()]

    @classmethod
    def getvalue(cls, line, attr):
        "get value from line."
        lne = ""
        index1 = line.find(f'{attr}="')
        if index1 == -1:
            return lne
        index1 += len(attr) + 2
        index2 = line.find('"', index1)
        if index2 == -1:
            index2 = line.find("/>", index1)
        if index2 == -1:
            return lne
        return Utils.cdata(line[index1:index2])

    @classmethod
    def getattrs(cls, line, token):
        "get attributes from line."
        index = 0
        result = []
        stop = False
        while not stop:
            index1 = line.find(f"<{token} ", index)
            if index1 == -1:
                return result
            index1 += len(token) + 2
            index2 = line.find("/>", index1)
            if index2 == -1:
                return result
            result.append(line[index1:index2])
            index = index2
        return result

    @classmethod
    def parse(cls, txt, toke="outline", itemz=None):
        "parse opml from text."
        if itemz is None:
            itemz = ",".join(cls.getnames(txt))
        for attrz in cls.getattrs(txt, toke):
            if not attrz:
                continue
            obj = {}
            for itm in Utils.spl(itemz):
                if itm == "link":
                    itm = "href"
                obj[itm] = cls.getvalue(attrz, itm)
            yield obj


def exp(event):
    "export opml."
    with Locks.importlock:
        event.reply(TEMPLATE)
        nrs = 0
        for _fn, ooo in Locater.find(Method.fqn(OPML)):
            nrs += 1
            obj = Rss()
            Method.update(obj, ooo)
            name = f"url{nrs}"
            dipl = obj.display_list
            url = obj.rss
            txt = f'<outline name="{name}" display_list="{dipl}" xmlUrl="{url}"/>'
            event.reply(" " * 12 + txt)
        event.reply(" " * 8 + "</outline>")
        event.reply("    <body>")
        event.reply("</opml>")


def imp(event):
    "import opml."
    if not event.args:
        event.iface("<filename>")
        return
    fnm = event.args[0]
    if not os.path.isfile(fnm):
        event.reply(f"no {fnm} file found.")
        return
    with Locks.importlock:
        with open(fnm, "r", encoding="utf-8") as file:
            txt = file.read()
        prs = OPML()
        nrs = 0
        nrskip = 0
        insertid = Utils.shortid()
        skipped = []
        for obj in prs.parse(txt, "outline", "name,xmlUrl"):
            url = obj["xmlUrl"]
            if url in skipped:
                continue
            if not url.startswith("http"):
                continue
            has = list(Locater.find(
                                   Method.fqn(OPML),
                                   {"rss": url},
                                   matching=True
                                  ))
            if has:
                skipped.append(url)
                nrskip += 1
                continue
            feed = Rss()
            feed.rss = obj["xmlUrl"]
            del obj["xmlUrl"]
            Method.update(feed, obj)
            uri = urllib.parse.urlparse(feed.rss)
            feed.name = max(uri.netloc.split("."), key=len)
            feed.insertid = insertid
            Disk.write(feed)
            nrs += 1
    if nrskip:
        event.reply(f"skipped {nrskip} urls.")
    if nrs:
        event.reply(f"added {nrs} urls.")


TEMPLATE = """<opml version="1.0">
    <head>
        <title>OPML</title>
    </head>
    <body>
        <outline title="opml" text="rss feeds">"""
