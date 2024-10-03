__all__ = ["process_settings"]

import typing

import markupsafe

from .cookies import delete_cookie, get_cookies, set_cookie
from .query import SettingsQuery

COOKIE_EXPIRY = 3 * 365  # Days


def process_settings() -> str | None:
    query = SettingsQuery.from_post_data()
    match query.action:
        case "set":
            return _do_set(query)
        case "delete":
            return _do_delete(query)
        case None:
            return None
        case _:
            typing.assert_never(query.action)


def _do_set(query: SettingsQuery) -> str | None:
    cookies = get_cookies()
    changes: set[str] = set()
    if query.lang:
        key = "CopyviosDefaultLang"
        if key not in cookies or cookies[key].value != query.lang:
            set_cookie(key, query.lang, COOKIE_EXPIRY)
            changes.add("site")
    if query.project:
        key = "CopyviosDefaultProject"
        if key not in cookies or cookies[key].value != query.project:
            set_cookie(key, query.project, COOKIE_EXPIRY)
            changes.add("site")
    if query.background:
        key = "CopyviosBackground"
        if key not in cookies or cookies[key].value != query.background:
            set_cookie(key, query.background, COOKIE_EXPIRY)
            delete_cookie("EarwigBackgroundCache")  # Old name
            changes.add("background")
    if changes:
        return f"Updated {', '.join(sorted(changes))}."
    return None


def _do_delete(query: SettingsQuery) -> str | None:
    cookies = get_cookies()
    cookie = query.cookie
    if cookie and cookie in cookies:
        delete_cookie(cookie)
        return f'Deleted cookie <b><span class="mono">{markupsafe.escape(cookie)}</span></b>.'
    elif query.all:
        number = len(cookies)
        for cookie in list(cookies.values()):
            delete_cookie(cookie.key)
        return f"Deleted <b>{number}</b> cookies."
    return None
