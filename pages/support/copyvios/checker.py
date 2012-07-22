# -*- coding: utf-8  -*-

from datetime import datetime
from hashlib import sha256
from time import time

from earwigbot import exceptions

from ..misc import open_sql_connection

def get_results(context, bot, site, title, url, query):
    page = site.get_page(title)
    try:
        page.get()  # Make sure that the page exists before we check it!
    except (exceptions.PageNotFoundError, exceptions.InvalidPageError):
        return page, None

    # if url:
    #     result = _get_url_specific_results(page, url)
    # else:
    #     conn = open_sql_connection(bot, "copyvioCache")
    #     if not query.get("nocache"):
    #         result = _get_cached_results(page, conn)
    #     if query.get("nocache") or not result:
    #         result = _get_fresh_results(page, conn)
    tstart = time()
    mc1 = __import__("earwigbot").wiki.copyvios.MarkovChain(page.get())
    mc2 = __import__("earwigbot").wiki.copyvios.MarkovChain(u"This is some random textual content for a page.")
    mci = __import__("earwigbot").wiki.copyvios.MarkovChainIntersection(mc1, mc2)
    result = __import__("earwigbot").wiki.copyvios.CopyvioCheckResult(
        True, 0.67123, "http://example.com/", 7, mc1, (mc2, mci))
    result.cached = False
    result.tdiff = time() - tstart
    # END TEST BLOCK
    return page, result

def _get_url_specific_results(page, url):
    t_start = time()
    result = page.copyvio_compare(url)
    result.cached = False
    result.tdiff = time() - t_start
    return result

def _get_cached_results(page, conn):
    query1 = "DELETE FROM cache WHERE cache_time < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)"
    query2 = "SELECT cache_url, cache_time, cache_queries, cache_process_time FROM cache WHERE cache_id = ? AND cache_hash = ?"
    pageid = page.pageid()
    hash = sha256(page.get()).hexdigest()
    t_start = time()

    with conn.cursor() as cursor:
        cursor.execute(query1)
        cursor.execute(query2, (pageid, hash))
        results = cursor.fetchall()
        if not results:
            return None

    url, cache_time, num_queries, original_tdiff = results[0]
    result = page.copyvio_compare(url)
    result.cached = True
    result.queries = num_queries
    result.tdiff = time() - t_start
    result.original_tdiff = original_tdiff
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

def _get_fresh_results(page, conn):
    t_start = time()
    result = page.copyvio_check(max_queries=10)
    result.cached = False
    result.tdiff = time() - t_start
    _cache_result(page, result, conn)
    return result

def _cache_result(page, result, conn):
    pageid = page.pageid()
    hash = sha256(page.get()).hexdigest()
    query1 = "SELECT 1 FROM cache WHERE cache_id = ?"
    query2 = "DELETE FROM cache WHERE cache_id = ?"
    query3 = "INSERT INTO cache VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)"
    with conn.cursor() as cursor:
        cursor.execute(query1, (pageid,))
        if cursor.fetchall():
            cursor.execute(query2, (pageid,))
        cursor.execute(query3, (pageid, hash, result.url, result.queries,
                                result.tdiff))
