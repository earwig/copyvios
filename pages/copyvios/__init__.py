# -*- coding: utf-8  -*-

from urlparse import parse_qs
from earwigbot.bot import Bot

from .checker import get_results
from .highlighter import highlight_delta
from ..support.sites import get_site, get_sites

def main(context, environ):
    lang = orig_lang = project = name = title = url = None
    site = page = result = None

    # Parse the query string.
    query = parse_qs(environ["QUERY_STRING"])
    if "lang" in query:
        lang = orig_lang = query["lang"][0].decode("utf8").lower()
        if "::" in lang:
            lang, name = lang.split("::", 1)
    if "project" in query:
        project = query["project"][0].decode("utf8").lower()
    if "title" in query:
        title = query["title"][0].decode("utf8")
    if "url" in query:
        url = query["url"][0].decode("utf8")

    bot = Bot(".earwigbot")
    all_langs, all_projects = get_sites(bot)
    if lang and project and title:
        site = get_site(bot, lang, project, name, all_projects)
        if site:
            page, result = get_results(bot, site, title, url, query)

    return lang, project, name, title, url, site, page, result
