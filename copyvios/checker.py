# -*- coding: utf-8  -*-

from datetime import datetime
from hashlib import sha256
from urlparse import urlparse

from earwigbot import exceptions
from earwigbot.wiki.copyvios.markov import EMPTY

from .misc import Query, get_cache_db
from .sites import get_site, get_sites

__all__ = ["do_check", "T_POSSIBLE", "T_SUSPECT"]

T_POSSIBLE = 0.4
T_SUSPECT = 0.75

def do_check():
    query = Query()
    if query.lang:
        query.lang = query.orig_lang = query.lang.lower()
        if "::" in query.lang:
            query.lang, query.name = query.lang.split("::", 1)
    if query.project:
        query.project = query.project.lower()

    query.all_langs, query.all_projects = get_sites()
    query.submitted = query.project and query.lang and (query.title or query.oldid)
    if query.submitted:
        query.site = get_site(query)
        if query.site:
            _get_results(query, follow=query.noredirect is None)
    return query

def _get_results(query, follow=True):
    if query.oldid:
        page = query.page = _get_page_by_revid(query.site, query.oldid)
        if not page:
            return
    else:
        page = query.page = query.site.get_page(query.title)
        try:
            page.get()  # Make sure that the page exists before we check it!
        except (exceptions.PageNotFoundError, exceptions.InvalidPageError):
            return
        if page.is_redirect and follow:
            try:
                query.title = page.get_redirect_target()
            except exceptions.RedirectError:
                pass  # Something's wrong. Continue checking the original page.
            else:
                query.redirected_from = page
                return _get_results(query, follow=False)

    if not query.action:
        query.action = "compare" if query.url else "search"
    if query.action == "search":
        conn = get_cache_db()
        use_engine = 1 if query.use_engine else 0
        use_links = 1 if query.use_links else 0
        mode = "{0}:{1}:".format(use_engine, use_links)
        if not query.nocache:
            query.result = _get_cached_results(page, conn, query, mode)
        if not query.result:
            query.result = page.copyvio_check(
                min_confidence=T_SUSPECT, max_queries=10, max_time=45,
                no_searches=not use_engine, no_links=not use_links)
            query.result.cached = False
            _cache_result(page, query.result, conn, mode)
    elif query.action == "compare":
        if not query.url:
            query.error = "no URL"
            return
        scheme = urlparse(query.url).scheme
        if not scheme and query.url[0] not in ":/":
            query.url = "http://" + query.url
        elif scheme not in ["http", "https"]:
            query.error = "bad URI"
            return
        result = _do_copyvio_compare(query, page, query.url)
        if result:
            query.result = result
            query.result.cached = False
    else:
        query.error = "bad action"

def _get_page_by_revid(site, revid):
    res = site.api_query(action="query", prop="info|revisions", revids=revid,
                         rvprop="content|timestamp", inprop="protection|url")
    try:
        page_data = res["query"]["pages"].values()[0]
        title = page_data["title"]
        page_data["revisions"][0]["*"]  # Only need to check that these exist
        page_data["revisions"][0]["timestamp"]
    except KeyError:
        return
    page = site.get_page(title)

    # EarwigBot doesn't understand old revisions of pages, so we use a somewhat
    # dirty hack to make this work:
    page._load_attributes(res)
    page._load_content(res)
    return page

def _get_cached_results(page, conn, query, mode):
    query1 = """DELETE FROM cache
                WHERE cache_time < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)"""
    query2 = """SELECT cache_url, cache_time, cache_queries, cache_process_time
                FROM cache
                WHERE cache_id = ? AND cache_hash = ?"""
    shahash = sha256(mode + page.get().encode("utf8")).hexdigest()

    with conn.cursor() as cursor:
        cursor.execute(query1)
        cursor.execute(query2, (page.pageid, shahash))
        results = cursor.fetchall()
        if not results:
            return None

    url, cache_time, num_queries, original_time = results[0]
    result = _do_copyvio_compare(query, page, url)
    if result:
        result.cached = True
        result.queries = num_queries
        result.original_time = original_time
        result.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
        result.cache_age = _format_date(cache_time)
    return result

def _do_copyvio_compare(query, page, url):
    result = page.copyvio_compare(url, min_confidence=T_SUSPECT, max_time=30)
    if result.source_chain is not EMPTY:
        return result
    query.error = "timeout" if result.time > 30 else "no data"

def _format_date(cache_time):
    diff = datetime.utcnow() - cache_time
    if diff.seconds > 3600:
        return "{0} hours".format(diff.seconds / 3600)
    if diff.seconds > 60:
        return "{0} minutes".format(diff.seconds / 60)
    return "{0} seconds".format(diff.seconds)

def _cache_result(page, result, conn, mode):
    query = """INSERT INTO cache
               VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
               ON DUPLICATE KEY UPDATE
               cache_url = ?, cache_time = CURRENT_TIMESTAMP,
               cache_queries = ?, cache_process_time = ?"""
    shahash = sha256(mode + page.get().encode("utf8")).hexdigest()
    args = (page.pageid, shahash, result.url, result.queries, result.time,
            result.url, result.queries, result.time)
    with conn.cursor() as cursor:
        cursor.execute(query, args)
