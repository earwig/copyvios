# -*- coding: utf-8  -*-

from datetime import datetime, timedelta
from hashlib import sha256
from logging import getLogger
from urlparse import urlparse

from earwigbot import exceptions
from earwigbot.wiki.copyvios.markov import EMPTY, MarkovChain
from earwigbot.wiki.copyvios.parsers import ArticleTextParser
from earwigbot.wiki.copyvios.result import CopyvioSource, CopyvioCheckResult

from .misc import Query, get_db, get_cursor, get_sql_error, sql_dialect
from .sites import get_site
from .turnitin import search_turnitin

__all__ = ["do_check", "T_POSSIBLE", "T_SUSPECT"]

T_POSSIBLE = 0.4
T_SUSPECT = 0.75

_LOGGER = getLogger("copyvios.checker")

def _coerce_bool(val):
    return val and val not in ("0", "false")

def do_check(query=None):
    if not query:
        query = Query()
    if query.lang:
        query.lang = query.orig_lang = query.lang.lower()
        if "::" in query.lang:
            query.lang, query.name = query.lang.split("::", 1)
    if query.project:
        query.project = query.project.lower()

    query.submitted = query.project and query.lang and (query.title or query.oldid)
    if query.submitted:
        query.site = get_site(query)
        if query.site:
            _get_results(query, follow=not _coerce_bool(query.noredirect))
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
                _get_results(query, follow=False)
                return

    if not query.action:
        query.action = "compare" if query.url else "search"
    if query.action == "search":
        use_engine = 0 if query.use_engine in ("0", "false") else 1
        use_links = 0 if query.use_links in ("0", "false") else 1
        use_turnitin = 1 if query.turnitin in ("1", "true") else 0
        if not use_engine and not use_links and not use_turnitin:
            query.error = "no search method"
            return

        # Handle the turnitin check
        if use_turnitin:
            query.turnitin_result = search_turnitin(page.title, query.lang)

        # Handle the copyvio check
        _perform_check(query, page, use_engine, use_links)
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
        return None
    page = site.get_page(title)

    # EarwigBot doesn't understand old revisions of pages, so we use a somewhat
    # dirty hack to make this work:
    page._load_attributes(res)
    page._load_content(res)
    return page

def _perform_check(query, page, use_engine, use_links):
    conn = get_db()
    sql_error = get_sql_error()
    mode = "{0}:{1}:".format(use_engine, use_links)

    if not _coerce_bool(query.nocache):
        try:
            query.result = _get_cached_results(
                page, conn, mode, _coerce_bool(query.noskip))
        except sql_error:
            _LOGGER.exception("Failed to retrieve cached results")

    if not query.result:
        try:
            query.result = page.copyvio_check(
                min_confidence=T_SUSPECT, max_queries=8, max_time=45,
                no_searches=not use_engine, no_links=not use_links,
                short_circuit=not query.noskip)
        except exceptions.SearchQueryError as exc:
            query.error = "search error"
            query.exception = exc
            return
        query.result.cached = False
        try:
            _cache_result(page, query.result, conn, mode)
        except sql_error:
            _LOGGER.exception("Failed to cache results")

def _get_cached_results(page, conn, mode, noskip):
    query1 = """SELECT cache_time, cache_queries, cache_process_time,
                       cache_possible_miss
                FROM cache
                WHERE cache_id = ?"""
    query2 = """SELECT cdata_url, cdata_confidence, cdata_skipped, cdata_excluded
                FROM cache_data
                WHERE cdata_cache_id = ?"""
    cache_id = buffer(sha256(mode + page.get().encode("utf8")).digest())

    cursor = conn.cursor()
    cursor.execute(query1, (cache_id,))
    results = cursor.fetchall()
    if not results:
        return None
    cache_time, queries, check_time, possible_miss = results[0]
    if possible_miss and noskip:
        return None
    if not isinstance(cache_time, datetime):
        cache_time = datetime.utcfromtimestamp(cache_time)
    if datetime.utcnow() - cache_time > timedelta(days=3):
        return None
    cursor.execute(query2, (cache_id,))
    data = cursor.fetchall()

    if not data:  # TODO: do something less hacky for this edge case
        article_chain = MarkovChain(ArticleTextParser(page.get()).strip())
        result = CopyvioCheckResult(False, [], queries, check_time,
                                    article_chain, possible_miss)
        result.cached = True
        result.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
        result.cache_age = _format_date(cache_time)
        return result

    url, confidence, skipped, excluded = data.pop(0)
    if skipped:  # Should be impossible: data must be bad; run a new check
        return None
    result = page.copyvio_compare(url, min_confidence=T_SUSPECT, max_time=30)
    if abs(result.confidence - confidence) >= 0.0001:
        return None

    for url, confidence, skipped, excluded in data:
        if noskip and skipped:
            return None
        source = CopyvioSource(None, url)
        source.confidence = confidence
        source.skipped = bool(skipped)
        source.excluded = bool(excluded)
        result.sources.append(source)
    result.queries = queries
    result.time = check_time
    result.possible_miss = possible_miss
    result.cached = True
    result.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
    result.cache_age = _format_date(cache_time)
    return result

def _format_date(cache_time):
    formatter = lambda n, w: "{0} {1}{2}".format(n, w, "" if n == 1 else "s")
    diff = datetime.utcnow() - cache_time
    total_seconds = diff.days * 86400 + diff.seconds
    if total_seconds > 3600:
        return formatter(total_seconds / 3600, "hour")
    if total_seconds > 60:
        return formatter(total_seconds / 60, "minute")
    return formatter(total_seconds, "second")

def _cache_result(page, result, conn, mode):
    expiry = sql_dialect(mysql="DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)",
                         sqlite="STRFTIME('%s', 'now', '-3 days')")
    query1 = "DELETE FROM cache WHERE cache_id = ?"
    query2 = "DELETE FROM cache WHERE cache_time < %s" % expiry
    query3 = """INSERT INTO cache (cache_id, cache_queries, cache_process_time,
                                   cache_possible_miss) VALUES (?, ?, ?, ?)"""
    query4 = """INSERT INTO cache_data (cdata_cache_id, cdata_url,
                                        cdata_confidence, cdata_skipped,
                                        cdata_excluded) VALUES (?, ?, ?, ?, ?)"""
    cache_id = buffer(sha256(mode + page.get().encode("utf8")).digest())
    data = [(cache_id, source.url[:1024], source.confidence, source.skipped,
             source.excluded)
            for source in result.sources]
    with get_cursor(conn) as cursor:
        cursor.execute(query1, (cache_id,))
        cursor.execute(query2)
        cursor.execute(query3, (cache_id, result.queries, result.time,
                                result.possible_miss))
        cursor.executemany(query4, data)
