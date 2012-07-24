# -*- coding: utf-8  -*-

from markupsafe import escape

from .cookies import parse_cookies, set_cookie, delete_cookie
from .misc import get_bot, Query
from .sites import get_sites

def main(context, environ, headers):
    query = Query(environ, method="POST")
    cookies = parse_cookies(context, environ)

    if query.action == "set":
        status = _do_set(query, cookies)
    elif query.action == "delete":
        status = _do_delete(query, cookies)
    else:
        status = None

    bot = get_bot()
    langs, projects = get_sites(bot)
    return bot, cookies, status, langs, projects

def _do_set(query, cookies):
    changes = set()
    if query.lang:
        key = "EarwigDefaultLang"
        if key not in cookies or cookies[key].value != query.lang:
            set_cookie(headers, cookies, key, query.lang, 365)
            changes.add("site")
    if query.project:
        key = "EarwigDefaultProject"
        if key not in cookies or cookies[key].value != query.project:
            set_cookie(headers, cookies, key, query.project, 365)
            changes.add("site")
    if changes:
        changes = ", ".format(changes)
        return "Updated {0}.".format(changes)
    return None

def _do_delete(query, cookies):
    if query.cookie in cookies:
        delete_cookie(headers, cookies, query.cookie.encode("utf8"))
        template = "Deleted cookie <b><tt>{0}</tt></b>."
        return template.format(escape(query.cookie))
    elif query.all:
        number = len(cookies)
        for cookie in cookies.values():
            delete_cookie(headers, cookies, cookie.key)
        return "Deleted <b>{0}</b> cookies.".format(number)
    return None
