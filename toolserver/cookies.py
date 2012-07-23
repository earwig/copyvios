# -*- coding: utf-8  -*-

import base64
from Cookie import BaseCookie
from datetime import datetime, timedelta
from os import path

class _CookieManager(BaseCookie):
    def __init__(self, environ):
        self._path = path.split(environ["PATH_INFO"])[0]
        try:
            self.load(environ["HTTP_COOKIE"])
        except AttributeError:
            pass

    def value_decode(self, value):
        try:
            return base64.b64decode(value).decode("utf8")
        except (TypeError, UnicodeDecodeError):
            return u"False"

    def value_encode(self, value):
        return base64.b64encode(value.encode("utf8"))

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
