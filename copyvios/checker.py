# -*- coding: utf-8  -*-

from datetime import datetime
from hashlib import sha256
from urlparse import urlparse

from earwigbot import exceptions

from .misc import get_bot, Query, open_sql_connection
from .sites import get_site, get_sites

def do_check():
    query = Query()
    if query.lang:
        query.lang = query.orig_lang = query.lang.lower()
        if "::" in query.lang:
            query.lang, query.name = query.lang.split("::", 1)
    if query.project:
        query.project = query.project.lower()

    query.bot = get_bot()
    query.all_langs, query.all_projects = get_sites(query.bot)
    if query.project and query.lang and query.title:  # TODO: and (query.title or query.oldid): ...
        query.site = get_site(query)
        if query.site:
            _get_results(query)
    return query

def _get_results(query):
    page = query.page = query.site.get_page(query.title)
    try:
        page.get()  # Make sure that the page exists before we check it!
    except (exceptions.PageNotFoundError, exceptions.InvalidPageError):
        return

    if query.url:
        if urlparse(query.url).scheme not in ["http", "https"]:
            query.error = "bad URI"
            return
        query.result = page.copyvio_compare(query.url)
        query.result.cached = False
    else:
        conn = open_sql_connection(query.bot, "cache")
        if not query.nocache:
            query.result = _get_cached_results(page, conn)
        if not query.result:
            query.result = page.copyvio_check(max_queries=10, max_time=45)
            query.result.cached = False
            _cache_result(page, query.result, conn)

def _get_cached_results(page, conn):
    query1 = "DELETE FROM cache WHERE cache_time < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)"
    query2 = "SELECT cache_url, cache_time, cache_queries, cache_process_time FROM cache WHERE cache_id = ? AND cache_hash = ?"
    shahash = sha256(page.get().encode("utf8")).hexdigest()

    with conn.cursor() as cursor:
        cursor.execute(query1)
        cursor.execute(query2, (page.pageid, shahash))
        results = cursor.fetchall()
        if not results:
            return None

    url, cache_time, num_queries, original_time = results[0]
    result = page.copyvio_compare(url)
    result.cached = True
    result.queries = num_queries
    result.original_time = original_time
    result.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
    result.cache_age = _format_date(cache_time)
    return result

def _format_date(cache_time):
    diff = datetime.utcnow() - cache_time
    if diff.seconds > 3600:
        return "{0} hours".format(diff.seconds / 3600)
    if diff.seconds > 60:
        return "{0} minutes".format(diff.seconds / 60)
    return "{0} seconds".format(diff.seconds)

def _cache_result(page, result, conn):
    pageid = page.pageid
    shahash = sha256(page.get().encode("utf8")).hexdigest()
    query1 = "SELECT 1 FROM cache WHERE cache_id = ?"
    query2 = "DELETE FROM cache WHERE cache_id = ?"
    query3 = "INSERT INTO cache VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)"
    with conn.cursor() as cursor:
        cursor.execute(query1, (pageid,))
        if cursor.fetchall():
            cursor.execute(query2, (pageid,))
        cursor.execute(query3, (pageid, shahash, result.url, result.queries,
                                result.time))
