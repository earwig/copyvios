# -*- coding: utf-8  -*-

from datetime import datetime
from hashlib import sha256
from urlparse import urlparse

from earwigbot import exceptions
from earwigbot.wiki.copyvios.markov import EMPTY, MarkovChain
from earwigbot.wiki.copyvios.parsers import ArticleTextParser
from earwigbot.wiki.copyvios.result import CopyvioSource, CopyvioCheckResult

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
        use_engine = 0 if query.use_engine == "0" else 1
        use_links = 0 if query.use_links == "0" else 1
        if not use_engine and not use_links:
            query.error = "no search method"
            return
        mode = "{0}:{1}:".format(use_engine, use_links)
        if not query.nocache:
            query.result = _get_cached_results(page, conn, mode)
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
        result = page.copyvio_compare(query.url, min_confidence=T_SUSPECT,
                                      max_time=30)
        if result.best.chains[0] is EMPTY:
            query.error = "timeout" if result.time > 30 else "no data"
            return
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

def _get_cached_results(page, conn, mode):
    query1 = """DELETE FROM cache
                WHERE cache_time < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)"""
    query2 = """SELECT cache_time, cache_queries, cache_process_time
                FROM cache
                WHERE cache_id = ?"""
    query3 = """SELECT cdata_url, cdata_confidence, cdata_skipped
                FROM cache_data
                WHERE cdata_cache_id = ?"""
    cache_id = buffer(sha256(mode + page.get().encode("utf8")).digest())

    with conn.cursor() as cursor:
        cursor.execute(query1)
        cursor.execute(query2, (cache_id,))
        results = cursor.fetchall()
        if not results:
            return None
        cache_time, queries, check_time = results[0]
        cursor.execute(query3, (cache_id,))
        data = cursor.fetchall()

    if not data:  # TODO: do something less hacky for this edge case
        artchain = MarkovChain(ArticleTextParser(page.get()).strip())
        result = CopyvioCheckResult(False, [], queries, check_time, artchain)
        result.cached = True
        result.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
        result.cache_age = _format_date(cache_time)
        return result

    url, confidence, skipped = data.pop(0)
    if skipped:  # Should be impossible: data must be bad; run a new check
        return None
    result = page.copyvio_compare(url, min_confidence=T_SUSPECT, max_time=30)
    if abs(result.confidence - confidence) < 0.0001:
        return None

    for url, confidence, skipped in data:
        source = CopyvioSource(None, url)
        source.confidence = confidence
        source.skipped = bool(skipped)
        result.sources.append(source)
    result.queries = queries
    result.time = check_time
    result.cached = True
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

def _cache_result(page, result, conn, mode):
    query1 = "DELETE FROM cache WHERE cache_id = ?"
    query2 = "INSERT INTO cache VALUES (?, DEFAULT, ?, ?)"
    query3 = "INSERT INTO cache_data VALUES (DEFAULT, ?, ?, ?, ?)"
    cache_id = buffer(sha256(mode + page.get().encode("utf8")).digest())
    data = [(cache_id, source.url, source.confidence, source.skipped)
            for source in result.sources]
    with conn.cursor() as cursor:
        cursor.execute("START TRANSACTION")
        cursor.execute(query1, (cache_id,))
        cursor.execute(query2, (cache_id, result.queries, result.time))
        cursor.executemany(query3, data)
        cursor.execute("COMMIT")
