# -*- coding: utf-8  -*-

from .checker import get_results
from .highlighter import highlight_delta
from .misc import get_bot, Query
from .sites import get_site, get_sites

def main(context, environ):
    query = Query(environ)
    if query.lang:
        query.lang = query.orig_lang = query.lang.lower()
        if "::" in query.lang:
            query.lang, query.name = query.lang.split("::", 1)
    if query.project:
        query.project = query.project.lower()

    query.bot = get_bot()
    query.all_langs, query.all_projects = get_sites(query.bot)
    if query.lang and query.project and query.title:
        query.site = get_site(query)
        if query.site:
            get_results(query)
    return query
