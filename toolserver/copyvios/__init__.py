# -*- coding: utf-8  -*-

from .checker import get_results
from .highlighter import highlight_delta
from ..misc import get_bot, Query
from ..sites import get_site, get_sites

def main(context, environ):
    query = Query(environ)
    if query.lang:
        query.lang = query.orig_lang = query.lang.lower()
        if "::" in query.lang:
            query.lang, query.name = query.lang.split("::", 1)
    if query.project:
        query.project = query.project.lower()

    bot = get_bot(context)
    all_langs, all_projects = get_sites(context, bot)
    page = result = None
    if query.lang and query.project and query.title:
        site = get_site(bot, query, all_projects)
        if site:
            page, result = get_results(bot, site, query)

    return query, bot, all_langs, all_projects, page, result
