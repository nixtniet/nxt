# This file is placed in the Public Domain.


"fectch feeds"


import urllib
import urllib.parse
import urllib.request


from .objects import Data, Method


class Fetcher:

    modified = {}
    skip = [
        '403',
        '404',
        '410',
        '500',
        '503',
        'not valid',
        'not known',
        'failed'
    ]

    @classmethod
    def doskip(cls, errs):
        "check whether to log."
        for error in cls.skip:
            if error in errs:
                return True
        return False

    @classmethod
    def geturl(cls, url, force=False):
        "fetch an url."
        url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
        req = urllib.request.Request(str(url))
        req.add_header("User-Agent", cls.useragent("RSS Fetcher"))
        since = cls.modified.get(url, "")
        if since:
            req.add_header('If-Modified-Since', since)
        response = Data()
        try:
            Method.update(response, cls.request(req))
        except Exception as ex:
            response.data = []
            response.error = str(ex)
            response.headers = req.headers
        return response

    @classmethod
    def request(cls, req):
        with urllib.request.urlopen(req, timeout=3) as response:  # nosec
            modi = response.headers.get('Last-Modified', "")
            if modi:
                cls.modified[req.get_full_url()] = modi
            response.data = response.read()
            response.error = ""
            return response

    @classmethod
    def useragent(cls, txt):
        "produce useragent string."
        return "Mozilla/5.0 (X11; Linux x86_64) " + txt


def __dir__():
    return (
        'Fetcher',
    )
