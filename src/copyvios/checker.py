__all__ = ["T_POSSIBLE", "T_SUSPECT", "do_check"]

import hashlib
import logging
import re
import typing
import urllib.parse
from datetime import UTC, datetime, timedelta
from enum import Enum

from earwigbot import exceptions
from earwigbot.wiki import Page, Site
from earwigbot.wiki.copyvios import CopyvioChecker
from earwigbot.wiki.copyvios.markov import DEFAULT_DEGREE, EMPTY
from earwigbot.wiki.copyvios.result import CopyvioCheckResult, CopyvioSource
from earwigbot.wiki.copyvios.workers import CopyvioWorkspace
from flask import g
from sqlalchemy import PoolProxiedConnection

from .cache import cache
from .misc import get_sql_error, sql_dialect
from .query import CheckQuery
from .sites import get_site
from .turnitin import search_turnitin

T_POSSIBLE = 0.4
T_SUSPECT = 0.75

_LOGGER = logging.getLogger("copyvios.checker")


class ErrorCode(Enum):
    BAD_ACTION = "bad action"
    BAD_OLDID = "bad oldid"
    BAD_URI = "bad URI"
    NO_DATA = "no data"
    NO_SEARCH_METHOD = "no search method"
    NO_URL = "no URL"
    SEARCH_ERROR = "search error"
    TIMEOUT = "timeout"


class CopyvioCheckError(Exception):
    def __init__(self, code: ErrorCode):
        super().__init__(code.value)
        self.code = code


def do_check(query: CheckQuery) -> CopyvioCheckResult | None:
    if query.submitted:
        site = get_site(query)
        if site:
            return _get_results(query, site, follow=not query.noredirect)
    return None


def _get_results(
    query: CheckQuery, site: Site, follow: bool = True
) -> CopyvioCheckResult | None:
    if query.oldid:
        if not re.match(r"^\d+$", query.oldid):
            raise CopyvioCheckError(ErrorCode.BAD_OLDID)
        page = _get_page_by_revid(site, query.oldid)
        if not page:
            return None
        g.page = page
    else:
        assert query.title
        g.page = page = site.get_page(query.title)
        try:
            page.get()  # Make sure that the page exists before we check it
        except (exceptions.PageNotFoundError, exceptions.InvalidPageError):
            return None
        if page.is_redirect and follow:
            try:
                query.title = page.get_redirect_target()
            except exceptions.RedirectError:
                pass  # Something's wrong; continue checking the original page
            else:
                result = _get_results(query, site, follow=False)
                if result:
                    result.metadata.redirected_from = page
                return result

    if not query.action:
        query.action = "compare" if query.url else "search"

    if query.action == "search":
        if not query.use_engine and not query.use_links and not query.turnitin:
            raise CopyvioCheckError(ErrorCode.NO_SEARCH_METHOD)

        # Handle the Turnitin check
        turnitin_result = None
        if query.turnitin:
            assert query.lang
            turnitin_result = search_turnitin(page.title, query.lang)

        # Handle the copyvio check
        conn = cache.engine.raw_connection()
        try:
            result = _perform_check(query, page, conn)
        finally:
            conn.close()
        result.metadata.turnitin_result = turnitin_result

    elif query.action == "compare":
        if not query.url:
            raise CopyvioCheckError(ErrorCode.NO_URL)
        scheme = urllib.parse.urlparse(query.url).scheme
        if not scheme and query.url[0] not in ":/":
            query.url = "http://" + query.url
        elif scheme not in ["http", "https"]:
            raise CopyvioCheckError(ErrorCode.BAD_URI)

        degree = query.degree or DEFAULT_DEGREE
        result = page.copyvio_compare(
            query.url, min_confidence=T_SUSPECT, max_time=10, degree=degree
        )
        result.metadata.cached = False

        if not result.best or result.best.chains[0] is EMPTY:
            if result.time > 10:
                raise CopyvioCheckError(ErrorCode.TIMEOUT)
            else:
                raise CopyvioCheckError(ErrorCode.NO_DATA)
        return result

    else:
        raise CopyvioCheckError(ErrorCode.BAD_ACTION)


def _get_page_by_revid(site: Site, revid: str) -> Page | None:
    try:
        res = site.api_query(
            action="query",
            prop="info|revisions",
            revids=revid,
            rvprop="content|timestamp",
            inprop="protection|url",
            rvslots="main",
        )
        page_data = list(res["query"]["pages"].values())[0]
        title = page_data["title"]
        # Only need to check that these exist:
        revision = page_data["revisions"][0]
        revision["slots"]["main"]["*"]
        revision["timestamp"]
    except (exceptions.APIError, KeyError, IndexError):
        return None
    page = site.get_page(title)

    # EarwigBot doesn't understand old revisions of pages, so we use a somewhat
    # dirty hack to make this work:
    page._load_attributes(res)
    page._load_content(res)
    return page


def _perform_check(
    query: CheckQuery, page: Page, conn: PoolProxiedConnection
) -> CopyvioCheckResult:
    sql_error = get_sql_error()
    mode = f"{query.use_engine}:{query.use_links}:"
    result: CopyvioCheckResult | None = None

    if not query.nocache:
        try:
            result = _get_cached_results(page, conn, mode, query.noskip)
        except sql_error:
            _LOGGER.exception("Failed to retrieve cached results")

    if not result:
        try:
            result = page.copyvio_check(
                min_confidence=T_SUSPECT,
                max_queries=8,
                max_time=30,
                no_searches=not query.use_engine,
                no_links=not query.use_links,
                short_circuit=not query.noskip,
            )
        except exceptions.SearchQueryError as exc:
            raise CopyvioCheckError(ErrorCode.SEARCH_ERROR) from exc
        result.metadata.cached = False
        try:
            _cache_result(page, result, conn, mode)
        except sql_error:
            _LOGGER.exception("Failed to cache results")

    return result


def _get_cache_id(page: Page, mode: str) -> bytes:
    return hashlib.sha256((mode + page.get()).encode("utf8")).digest()


def _get_cached_results(
    page: Page, conn: PoolProxiedConnection, mode: str, noskip: bool
) -> CopyvioCheckResult | None:
    cache_id = _get_cache_id(page, mode)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT cache_time, cache_queries, cache_process_time, cache_possible_miss
        FROM cache
        WHERE cache_id = ?""",
        (cache_id,),
    )
    results = cursor.fetchall()

    if not results:
        return None
    cache_time, queries, check_time, possible_miss = results[0]
    if possible_miss and noskip:
        return None

    if not isinstance(cache_time, datetime):
        cache_time = datetime.fromtimestamp(cache_time, tz=UTC)
    elif cache_time.tzinfo is None:
        cache_time = cache_time.replace(tzinfo=UTC)
    if datetime.now(UTC) - cache_time > timedelta(days=3):
        return None

    cursor.execute(
        """SELECT cdata_url, cdata_confidence, cdata_skipped, cdata_excluded
        FROM cache_data
        WHERE cdata_cache_id = ?""",
        (cache_id,),
    )
    data = cursor.fetchall()

    if not data:  # TODO: Do something less hacky for this edge case
        article_chain = CopyvioChecker(page).article_chain
        result = CopyvioCheckResult(
            False, [], queries, check_time, article_chain, possible_miss
        )
        result.metadata.cached = True
        result.metadata.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
        result.metadata.cache_age = _format_date(cache_time)
        return result

    url, confidence, skipped, excluded = data[0]
    if skipped:  # Should be impossible: data must be bad; run a new check
        return None
    result = page.copyvio_compare(url, min_confidence=T_SUSPECT, max_time=10)
    if abs(result.confidence - confidence) >= 0.0001:
        return None

    for url, confidence, skipped, excluded in data[1:]:
        if noskip and skipped:
            return None
        source = CopyvioSource(typing.cast(CopyvioWorkspace, None), url)
        source.confidence = confidence
        source.skipped = bool(skipped)
        source.excluded = bool(excluded)
        result.sources.append(source)

    result.queries = queries
    result.time = check_time
    result.possible_miss = possible_miss
    result.metadata.cached = True
    result.metadata.cache_time = cache_time.strftime("%b %d, %Y %H:%M:%S UTC")
    result.metadata.cache_age = _format_date(cache_time)
    return result


def _format_date(cache_time: datetime) -> str:
    def formatter(val: float, unit: str):
        return f"{int(val)} {unit}{'' if val == 1 else 's'}"

    diff = datetime.now(UTC) - cache_time
    total_seconds = diff.days * 86400 + diff.seconds
    if total_seconds > 3600:
        return formatter(total_seconds / 3600, "hour")
    if total_seconds > 60:
        return formatter(total_seconds / 60, "minute")
    return formatter(total_seconds, "second")


def _cache_result(
    page: Page, result: CopyvioCheckResult, conn: PoolProxiedConnection, mode: str
) -> None:
    expiry = sql_dialect(
        mysql="DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)",
        sqlite="STRFTIME('%s', 'now', '-3 days')",
    )
    cache_id = _get_cache_id(page, mode)
    data = [
        (
            cache_id,
            source.url[:1024],
            source.confidence,
            source.skipped,
            source.excluded,
        )
        for source in result.sources
    ]

    # TODO: Switch to proper SQLAlchemy
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM cache WHERE cache_id = ?", (cache_id,))
        cur.execute(f"DELETE FROM cache WHERE cache_time < {expiry}")
        cur.execute(
            """INSERT INTO cache (
                cache_id, cache_queries, cache_process_time, cache_possible_miss
            ) VALUES (?, ?, ?, ?)""",
            (cache_id, result.queries, result.time, result.possible_miss),
        )
        cur.executemany(
            """INSERT INTO cache_data (
                cdata_cache_id, cdata_url, cdata_confidence, cdata_skipped,
                cdata_excluded
            ) VALUES (?, ?, ?, ?, ?)""",
            data,
        )
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        cur.close()
