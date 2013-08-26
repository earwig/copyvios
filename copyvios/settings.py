# -*- coding: utf-8  -*-

from markupsafe import escape

from .cookies import set_cookie, delete_cookie
from .misc import get_bot, Query
from .sites import get_sites

def main(context, environ, headers, cookies):
    query = Query(environ, method="POST")
    if query.action == "set":
        status = _do_set(query, headers, cookies)
    elif query.action == "delete":
        status = _do_delete(query, headers, cookies)
    else:
        status = None

    bot = get_bot()
    langs, projects = get_sites(bot)
    return bot, status, langs, projects

def _do_set(query, headers, cookies):
    changes = set()
    if query.lang:
        key = "CopyviosDefaultLang"
        if key not in cookies or cookies[key].value != query.lang:
            set_cookie(headers, cookies, key, query.lang, 1095)
            changes.add("site")
    if query.project:
        key = "CopyviosDefaultProject"
        if key not in cookies or cookies[key].value != query.project:
            set_cookie(headers, cookies, key, query.project, 1095)
            changes.add("site")
    if query.background:
        key = "CopyviosBackground"
        if key not in cookies or cookies[key].value != query.background:
            set_cookie(headers, cookies, key, query.background, 1095)
            delete_cookie(headers, cookies, "EarwigBackgroundCache")
            changes.add("background")
    if changes:
        changes = ", ".join(sorted(list(changes)))
        return "Updated {0}.".format(changes)
    return None

def _do_delete(query, headers, cookies):
    if query.cookie in cookies:
        delete_cookie(headers, cookies, query.cookie.encode("utf8"))
        template = u'Deleted cookie <b><span class="mono">{0}</span></b>.'
        return template.format(escape(query.cookie))
    elif query.all:
        number = len(cookies)
        for cookie in cookies.values():
            delete_cookie(headers, cookies, cookie.key)
        return "Deleted <b>{0}</b> cookies.".format(number)
    return None
