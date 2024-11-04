#! /usr/bin/env python

import functools
import hashlib
import json
import os
import time
import traceback
from typing import Any

from earwigbot.wiki.copyvios import globalize
from flask import Response, make_response, render_template, request

from copyvios import app
from copyvios.api import format_api_error, handle_api_request
from copyvios.attribution import get_attribution_info
from copyvios.background import get_background
from copyvios.cache import cache
from copyvios.checker import (
    T_POSSIBLE,
    T_SUSPECT,
    CopyvioCheckError,
    ErrorCode,
    do_check,
)
from copyvios.cookies import get_cookies, get_new_cookies
from copyvios.highlighter import highlight_delta
from copyvios.misc import get_notice, get_permalink
from copyvios.query import CheckQuery
from copyvios.settings import process_settings
from copyvios.sites import update_sites

AnyResponse = Response | str | bytes

app.logger.info(f"Flask server started {time.asctime()}")

globalize(num_workers=8)


@app.errorhandler(Exception)
def handle_errors(exc: Exception) -> AnyResponse:
    if app.debug:
        raise  # Use built-in debugger
    app.logger.exception("Caught exception:")
    return render_template("error.html.jinja", traceback=traceback.format_exc())


@app.context_processor
def setup_context() -> dict[str, Any]:
    return {
        "T_POSSIBLE": T_POSSIBLE,
        "T_SUSPECT": T_SUSPECT,
        "ErrorCode": ErrorCode,
        "cache": cache,
        "dump_json": json.dumps,
        "get_attribution_info": get_attribution_info,
        "get_background": get_background,
        "get_cookies": get_cookies,
        "get_notice": get_notice,
        "get_permalink": get_permalink,
        "highlight_delta": highlight_delta,
    }


@app.after_request
def add_new_cookies(response: Response) -> Response:
    for cookie in get_new_cookies():
        response.headers.add("Set-Cookie", cookie)
    return response


@app.after_request
def write_access_log(response: Response) -> Response:
    app.logger.debug(
        f"{time.asctime()} {request.method} {request.path} "
        f"{request.values.to_dict()} -> {response.status_code}"
    )
    return response


@functools.lru_cache
def _get_hash(path: str, mtime: float) -> str:
    # mtime is used as part of the cache key
    with open(path, "rb") as fp:
        return hashlib.sha1(fp.read()).hexdigest()


def external_url_handler(
    error: Exception, endpoint: str, values: dict[str, Any]
) -> str:
    if endpoint == "static" and "file" in values:
        assert app.static_folder is not None
        path = os.path.join(app.static_folder, values["file"])
        mtime = os.path.getmtime(path)
        hashstr = _get_hash(path, mtime)
        return f"/static/{values['file']}?v={hashstr}"
    raise error


app.url_build_error_handlers.append(external_url_handler)


@app.route("/")
def index() -> AnyResponse:
    update_sites()
    query = CheckQuery.from_get_args()
    try:
        result = do_check(query)
        error = None
    except CopyvioCheckError as exc:
        app.logger.exception(f"Copyvio check failed on {query}")
        result = None
        error = exc

    return render_template(
        "index.html.jinja",
        query=query,
        result=result,
        error=error,
        splash=not result,
    )


@app.route("/settings", methods=["GET", "POST"])
def settings() -> AnyResponse:
    status = process_settings() if request.method == "POST" else None
    update_sites()
    return render_template(
        "settings.html.jinja",
        status=status,
        default_site=cache.bot.wiki.get_site(),
        splash=True,
    )


@app.route("/api")
def api() -> AnyResponse:
    return render_template("api_help.html.jinja")


@app.route("/api.json")
def api_json() -> AnyResponse:
    if not request.args:
        return render_template("api_help.html.jinja")

    format = request.args.get("format", "json")
    if format in ["json", "jsonfm"]:
        update_sites()
        try:
            result = handle_api_request()
        except Exception as exc:
            app.logger.exception("API request failed")
            result = format_api_error("unhandled_exception", exc)
    else:
        errmsg = f"Unknown format: {format!r}"
        result = format_api_error("unknown_format", errmsg)

    if format == "jsonfm":
        return render_template("api_result.html.jinja", result=result)
    resp = make_response(json.dumps(result))
    resp.mimetype = "application/json"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


if app.debug:
    # Silence browser 404s when testing
    @app.route("/favicon.ico")
    def favicon() -> AnyResponse:
        return app.send_static_file("favicon.ico")


if __name__ == "__main__":
    app.run()
