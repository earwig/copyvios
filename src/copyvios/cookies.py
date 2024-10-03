__all__ = [
    "delete_cookie",
    "get_cookies",
    "get_new_cookies",
    "parse_cookies",
    "set_cookie",
]

import base64
from datetime import UTC, datetime, timedelta
from http.cookies import CookieError, SimpleCookie

from flask import g, request


class CookieManager(SimpleCookie):
    MAGIC = "--cpv2"

    def __init__(self, path: str, cookies: str | None) -> None:
        self._path = path
        try:
            super().__init__(cookies)
        except CookieError:
            super().__init__()
        for cookie in list(self.keys()):
            if not self[cookie].value:
                del self[cookie]

    def value_decode(self, val: str) -> tuple[str, str]:
        unquoted = super().value_decode(val)[0]
        try:
            decoded = base64.b64decode(unquoted).decode()
        except (TypeError, ValueError):
            return "", ""
        if decoded.startswith(self.MAGIC):
            return decoded[len(self.MAGIC) :], val
        return "", ""

    def value_encode(self, val: str) -> tuple[str, str]:
        encoded = base64.b64encode((self.MAGIC + val).encode()).decode()
        quoted = super().value_encode(encoded)[1]
        return val, quoted

    @property
    def path(self) -> str:
        return self._path


def parse_cookies(path: str, cookies: str | None) -> CookieManager:
    return CookieManager(path, cookies)


def get_cookies() -> CookieManager:
    if "cookies" not in g:
        g.cookies = parse_cookies(
            request.script_root or "/", request.environ.get("HTTP_COOKIE")
        )
    assert isinstance(g.cookies, CookieManager), g.cookies
    return g.cookies


def get_new_cookies() -> list[str]:
    if "new_cookies" not in g:
        g.new_cookies = []
    assert isinstance(g.new_cookies, list), g.new_cookies
    return g.new_cookies


def set_cookie(key: str, value: str, days: float = 0) -> None:
    cookies = get_cookies()
    cookies[key] = value
    if days:
        expire_dt = datetime.now(UTC) + timedelta(days=days)
        expires = expire_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
        cookies[key]["expires"] = expires
    cookies[key]["path"] = cookies.path

    new_cookies = get_new_cookies()
    new_cookies.append(cookies[key].OutputString())


def delete_cookie(key: str) -> None:
    cookies = get_cookies()
    set_cookie(key, "", days=-1)
    del cookies[key]
