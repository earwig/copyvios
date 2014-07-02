# -*- coding: utf-8  -*-

import base64
from Cookie import CookieError, SimpleCookie
from datetime import datetime, timedelta

from flask import g

__all__ = ["parse_cookies", "set_cookie", "delete_cookie"]

class _CookieManager(SimpleCookie):
    MAGIC = "--cpv2"

    def __init__(self, path, cookies):
        self._path = path
        try:
            super(_CookieManager, self).__init__(cookies)
        except CookieError:
            super(_CookieManager, self).__init__()
        for cookie in self.keys():
            if self[cookie].value is False:
                del self[cookie]

    def value_decode(self, value):
        unquoted = super(_CookieManager, self).value_decode(value)[0]
        try:
            decoded = base64.b64decode(unquoted).decode("utf8")
        except (TypeError, UnicodeDecodeError):
            return False, "False"
        if decoded.startswith(self.MAGIC):
            return decoded[len(self.MAGIC):], value
        return False, "False"

    def value_encode(self, value):
        encoded = base64.b64encode(self.MAGIC + value.encode("utf8"))
        quoted = super(_CookieManager, self).value_encode(encoded)[1]
        return value, quoted

    @property
    def path(self):
        return self._path


def parse_cookies(path, cookies):
    return _CookieManager(path, cookies)

def set_cookie(key, value, days=0):
    g.cookies[key] = value
    if days:
        expire_dt = datetime.utcnow() + timedelta(days=days)
        expires = expire_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
        g.cookies[key]["expires"] = expires
    g.cookies[key]["path"] = g.cookies.path
    g.new_cookies.append(g.cookies[key].OutputString())

def delete_cookie(key):
    set_cookie(key, u"", days=-1)
    del g.cookies[key]
