#! /usr/bin/env python
import datetime
import functools
import hashlib
import json
import logging
import os
import time
import traceback
import urllib.parse
from collections.abc import Callable
from logging.handlers import TimedRotatingFileHandler
from typing import Any, ParamSpec

from earwigbot.wiki.copyvios import globalize
from flask import Flask, make_response, redirect, request, session
from flask_mako import MakoTemplates, TemplateError, render_template
from werkzeug import Response

from copyvios.api import format_api_error, handle_api_request
from copyvios.auth import clear_login_session, oauth_login_end, oauth_login_start
from copyvios.cache import cache
from copyvios.checker import CopyvioCheckError, ErrorCode, do_check
from copyvios.cookies import get_new_cookies
from copyvios.misc import get_notice
from copyvios.query import CheckQuery
from copyvios.settings import process_settings
from copyvios.sites import update_sites

app = Flask(__name__)
MakoTemplates(app)

app.config.from_pyfile("config.py", True)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)

hand = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
hand.setLevel(logging.DEBUG)
app.logger.addHandler(hand)
app.logger.info(f"Flask server started {time.asctime()}")

globalize(num_workers=8)

AnyResponse = Response | str | bytes
P = ParamSpec("P")


def catch_errors(func: Callable[P, AnyResponse]) -> Callable[P, AnyResponse]:
    @functools.wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> AnyResponse:
        try:
            return func(*args, **kwargs)
        except TemplateError as exc:
            app.logger.error(f"Caught exception:\n{exc.text}")
            return render_template("error.mako", traceback=exc.text)
        except Exception:
            app.logger.exception("Caught exception:")
            return render_template("error.mako", traceback=traceback.format_exc())

    return inner


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
@catch_errors
def index() -> AnyResponse:
    notice = get_notice()
    update_sites()
    query = CheckQuery.from_get_args()
    try:
        result = do_check(query)
        error = None
    except CopyvioCheckError as exc:
        if exc.code == ErrorCode.NOT_LOGGED_IN:
            target = "/login?next=" + urllib.parse.quote_plus(
                "/?" + request.query_string.decode(errors="ignore")
            )
            return redirect(target, 302)
        result = None
        error = exc
    return render_template(
        "index.mako",
        notice=notice,
        query=query,
        result=result,
        error=error,
    )


@app.route("/login", methods=["GET", "POST"])
@catch_errors
def login() -> AnyResponse:
    try:
        redirect_url = oauth_login_start() if request.method == "POST" else None
        if redirect_url:
            return redirect(redirect_url, 302)
    except Exception as e:
        app.logger.exception("OAuth login start failed")
        kwargs = {"error": str(e)}
    else:
        if session.get("username") is not None:
            return redirect("/", 302)
        kwargs = {"error": request.args.get("error")}
    return render_template("login.mako", **kwargs)


@app.route("/logout", methods=["GET", "POST"])
@catch_errors
def logout() -> AnyResponse:
    if request.method == "POST":
        clear_login_session()
        return redirect("/", 302)
    else:
        return render_template("logout.mako")


@app.route("/oauth-callback")
@catch_errors
def oauth_callback() -> AnyResponse:
    try:
        next_url = oauth_login_end()
    except Exception as e:
        app.logger.exception("OAuth login end failed")
        return redirect("/login?error=" + urllib.parse.quote_plus(str(e)), 302)
    else:
        return redirect(next_url, 302)


@app.route("/settings", methods=["GET", "POST"])
@catch_errors
def settings() -> AnyResponse:
    status = process_settings() if request.method == "POST" else None
    update_sites()
    default = cache.bot.wiki.get_site()
    kwargs = {
        "status": status,
        "default_lang": default.lang,
        "default_project": default.project,
    }
    return render_template("settings.mako", **kwargs)


@app.route("/api")
@catch_errors
def api() -> AnyResponse:
    return render_template("api.mako", help=True)


@app.route("/api.json")
@catch_errors
def api_json() -> AnyResponse:
    if not request.args:
        return render_template("api.mako", help=True)

    format = request.args.get("format", "json")
    if format in ["json", "jsonfm"]:
        update_sites()
        try:
            result = handle_api_request()
        except Exception as exc:
            result = format_api_error("unhandled_exception", exc)
    else:
        errmsg = f"Unknown format: {format!r}"
        result = format_api_error("unknown_format", errmsg)

    if format == "jsonfm":
        return render_template("api.mako", help=False, result=result)
    resp = make_response(json.dumps(result))
    resp.mimetype = "application/json"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


if __name__ == "__main__":
    app.run()
