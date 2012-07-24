# -*- coding: utf-8  -*-

from .cookies import parse_cookies, set_cookie, delete_cookie
from .misc import get_bot, Query
from .sites import get_sites

def main(context, environ, headers):
    cookies = parse_cookies(context, environ)
    query = Query(environ, method="POST")

    if query.action == "set":
        if query.lang:
            key = "EarwigDefaultLang"
            if key not in cookies or cookies[key].value != query.lang:
                set_cookie(headers, cookies, key, query.lang, 365)
        if query.project:
            key = "EarwigDefaultProject"
            if key not in cookies or cookies[key].value != query.project:
                set_cookie(headers, cookies, key, query.project, 365)
    elif query.action == "delete":
        if query.cookie in cookies:
            delete_cookie(headers, cookies, query.cookie)
        elif query.all:
            for cookie in cookies.values():
                if cookie.path.startswith(cookies.path):
                    delete_cookie(headers, cookies, cookie.key)

    bot = get_bot()
    langs, projects = get_sites(bot)
    return bot, cookies, langs, projects
