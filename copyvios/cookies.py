# -*- coding: utf-8  -*-

import base64
from Cookie import CookieError, SimpleCookie
from datetime import datetime, timedelta

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

def set_cookie(headers, cookies, key, value, days=0):
    cookies[key] = value
    if days:
        expires = datetime.utcnow() + timedelta(days=days)
        cookies[key]["expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    cookies[key]["path"] = cookies.path
    headers.append(("Set-Cookie", cookies[key].OutputString()))

def delete_cookie(headers, cookies, key):
    set_cookie(headers, cookies, key, u"", days=-1)
    del cookies[key]
