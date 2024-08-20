#! /usr/bin/env python
# -*- coding: utf-8  -*-

from functools import wraps
from hashlib import md5
from json import dumps
from logging import DEBUG, INFO, getLogger
from logging.handlers import TimedRotatingFileHandler
from os import path
from time import asctime
from traceback import format_exc

from earwigbot.bot import Bot
from earwigbot.wiki.copyvios import globalize
from flask import Flask, g, make_response, request
from flask_mako import MakoTemplates, render_template, TemplateError

from copyvios.api import format_api_error, handle_api_request
from copyvios.checker import do_check
from copyvios.cookies import parse_cookies
from copyvios.misc import cache, get_notice
from copyvios.settings import process_settings
from copyvios.sites import update_sites

app = Flask(__name__)
MakoTemplates(app)

hand = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
hand.setLevel(DEBUG)
app.logger.addHandler(hand)
app.logger.info(u"Flask server started " + asctime())
app._hash_cache = {}

def catch_errors(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TemplateError as exc:
            app.logger.error(u"Caught exception:\n{0}".format(exc.text))
            return render_template("error.mako", traceback=exc.text)
        except Exception:
            app.logger.exception(u"Caught exception:")
            return render_template("error.mako", traceback=format_exc())
    return inner

@app.before_first_request
def setup_app():
    cache.bot = Bot(".earwigbot", 100)
    cache.langs, cache.projects = [], []
    cache.last_sites_update = 0
    cache.background_data = {}
    cache.last_background_updates = {}

    globalize(num_workers=8)

@app.before_request
def prepare_request():
    g._db = None
    g.cookies = parse_cookies(
        request.script_root or "/", request.environ.get("HTTP_COOKIE"))
    g.new_cookies = []

@app.after_request
def add_new_cookies(response):
    for cookie in g.new_cookies:
        response.headers.add("Set-Cookie", cookie)
    return response

@app.after_request
def write_access_log(response):
    msg = u"%s %s %s %s -> %s"
    app.logger.debug(msg, asctime(), request.method, request.path,
                     request.values.to_dict(), response.status_code)
    return response

@app.teardown_appcontext
def close_databases(error):
    if g._db:
        g._db.close()

def external_url_handler(error, endpoint, values):
    if endpoint == "static" and "file" in values:
        fpath = path.join(app.static_folder, values["file"])
        mtime = path.getmtime(fpath)
        cache = app._hash_cache.get(fpath)
        if cache and cache[0] == mtime:
            hashstr = cache[1]
        else:
            with open(fpath, "rb") as f:
                hashstr = md5(f.read()).hexdigest()
            app._hash_cache[fpath] = (mtime, hashstr)
        return "/static/{0}?v={1}".format(values["file"], hashstr)
    raise error

app.url_build_error_handlers.append(external_url_handler)

@app.route("/")
@catch_errors
def index():
    notice = get_notice()
    update_sites()
    query = do_check()
    return render_template(
        "index.mako", notice=notice, query=query, result=query.result,
        turnitin_result=query.turnitin_result)

@app.route("/settings", methods=["GET", "POST"])
@catch_errors
def settings():
    status = process_settings() if request.method == "POST" else None
    update_sites()
    return render_template("settings.mako", status=status)

@app.route("/api")
@catch_errors
def api():
    return render_template("api.mako", help=True)

@app.route("/api.json")
@catch_errors
def api_json():
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
        errmsg = u"Unknown format: '{0}'".format(format)
        result = format_api_error("unknown_format", errmsg)

    if format == "jsonfm":
        return render_template("api.mako", help=False, result=result)
    resp = make_response(dumps(result))
    resp.mimetype = "application/json"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

if __name__ == '__main__':
    app.run()
