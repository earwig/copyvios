__all__ = ["format_api_error", "handle_api_request"]

from typing import Any

from earwigbot.wiki import Page
from earwigbot.wiki.copyvios.result import CopyvioCheckResult, CopyvioSource
from flask import g

from .cache import cache
from .checker import T_POSSIBLE, T_SUSPECT, CopyvioCheckError, ErrorCode, do_check
from .highlighter import highlight_delta
from .query import APIQuery
from .sites import get_site, update_sites

_CHECK_ERRORS = {
    ErrorCode.NO_SEARCH_METHOD: "Either 'use_engine' or 'use_links' must be true",
    ErrorCode.BAD_OLDID: "The revision ID is invalid",
    ErrorCode.NO_URL: "The parameter 'url' is required for URL comparisons",
    ErrorCode.BAD_URI: "The given URI scheme is unsupported",
    ErrorCode.NO_DATA: (
        "No text could be found in the given URL (note that only HTML and plain text "
        "pages are supported, and content generated by JavaScript or found inside "
        "iframes is ignored)"
    ),
    ErrorCode.TIMEOUT: "The given URL timed out before any data could be retrieved",
    ErrorCode.SEARCH_ERROR: (
        "An error occurred while using the search engine; try reloading or setting "
        "'use_engine' to 0"
    ),
}


def _serialize_page(page: Page) -> dict[str, Any]:
    return {"title": page.title, "url": page.url}


def _serialize_source(
    source: CopyvioSource | None, show_skip: bool = True
) -> dict[str, Any]:
    if not source:
        return {"url": None, "confidence": 0.0, "violation": "none"}

    if source.confidence >= T_SUSPECT:
        violation = "suspected"
    elif source.confidence >= T_POSSIBLE:
        violation = "possible"
    else:
        violation = "none"

    data = {
        "url": source.url,
        "confidence": source.confidence,
        "violation": violation,
    }
    if show_skip:
        data["skipped"] = source.skipped
        data["excluded"] = source.excluded
    return data


def _serialize_detail(result: CopyvioCheckResult) -> dict[str, Any] | None:
    if not result.best:
        return None
    source_chain, delta = result.best.chains
    article = highlight_delta(result.article_chain, delta)
    source = highlight_delta(source_chain, delta)
    return {"article": article, "source": source}


def format_api_error(code: str, info: Exception | str) -> dict[str, Any]:
    if isinstance(info, Exception):
        info = f"{type(info).__name__}: {info}"
    return {"status": "error", "error": {"code": code, "info": info}}


def _hook_default(query: APIQuery) -> dict[str, Any]:
    if query.action:
        return format_api_error(
            "unknown_action", f"Unknown action: {query.action.lower()!r}"
        )
    else:
        return format_api_error("missing_action", "Missing 'action' query parameter")


def _hook_check(query: APIQuery) -> dict[str, Any]:
    try:
        result = do_check(query)
    except CopyvioCheckError as exc:
        info = _CHECK_ERRORS.get(exc.code, "An unknown error occurred")
        return format_api_error(exc.code.name.lower(), info)

    if not query.submitted:
        info = (
            "The query parameters 'project', 'lang', and either 'title' or 'oldid' "
            "are required for checks"
        )
        return format_api_error("missing_params", info)
    if not get_site():
        info = (
            f"The given site (project={query.project}, lang={query.lang}) either "
            "doesn't exist, is closed, or is private"
        )
        return format_api_error("bad_site", info)
    if not result:
        if query.oldid:
            return format_api_error(
                "bad_oldid", f"The revision ID couldn't be found: {query.oldid}"
            )
        else:
            assert isinstance(g.page, Page), g.page
            return format_api_error(
                "bad_title", f"The page couldn't be found: {g.page.title}"
            )

    assert isinstance(g.page, Page), g.page
    data = {
        "status": "ok",
        "meta": {
            "time": result.time,
            "queries": result.queries,
            "cached": result.metadata.cached,
            "redirected": hasattr(result.metadata, "redirected_from"),
        },
        "page": _serialize_page(g.page),
    }
    if result.metadata.cached:
        data["meta"]["cache_time"] = result.metadata.cache_time
    if result.metadata.redirected_from:
        data["original_page"] = _serialize_page(result.metadata.redirected_from)
    data["best"] = _serialize_source(result.best, show_skip=False)
    data["sources"] = [_serialize_source(source) for source in result.sources]
    if query.detail:
        data["detail"] = _serialize_detail(result)
    return data


def _hook_sites(query: APIQuery) -> dict[str, Any]:
    update_sites()
    return {
        "status": "ok",
        "langs": [[lang.code, lang.name] for lang in cache.langs],
        "projects": [[project.code, project.name] for project in cache.projects],
    }


_HOOKS = {
    "compare": _hook_check,
    "search": _hook_check,
    "sites": _hook_sites,
}


def handle_api_request():
    query = APIQuery.from_get_args()

    if query.version == 1:
        action = query.action.lower() if query.action else ""
        return _HOOKS.get(action, _hook_default)(query)
    else:
        return format_api_error(
            "unsupported_version", f"The API version is unsupported: {query.version}"
        )
