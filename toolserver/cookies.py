# -*- coding: utf-8  -*-

import base64
from Cookie import CookieError, SimpleCookie
from datetime import datetime, timedelta
from os import path

class _CookieManager(SimpleCookie):
    def __init__(self, environ):
        self._path = path.split(environ["PATH_INFO"])[0]
        try:
            super(_CookieManager, self).__init__(environ["HTTP_COOKIE"])
        except (CookieError, AttributeError):
            super(_CookieManager, self).__init__()
        for cookie in self.keys():
            if self[cookie].value is False:
                del self[cookie]

    def value_decode(self, value):
        unquoted = super(_CookieManager, self).value_decode(value)[0]
        try:
            return base64.b64decode(unquoted).decode("utf8"), value
        except (TypeError, UnicodeDecodeError):
            return False, "False"

    def value_encode(self, value):
        encoded = base64.b64encode(value.encode("utf8"))
        quoted = super(_CookieManager, self).value_encode(encoded)[1]
        return value, encoded

    @property
    def path(self):
        return self._path


def parse_cookies(context, environ):
    return _CookieManager(environ)

def set_cookie(headers, cookies, key, value, days=0):
    cookies[key] = value
    if days:
        expires = datetime.utcnow() + timedelta(days=days)
        cookies[key]["expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    cookies[key]["path"] = cookies.path
    headers.append(("Set-Cookie", cookies[key].OutputString()))

def delete_cookie(headers, cookies, key):
    set_cookie(headers, cookies, key, "", days=-1)
