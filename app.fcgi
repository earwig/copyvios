#! /data/project/copyvios/env/bin/python
# -*- coding: utf-8  -*-

from functools import wraps
from json import dumps
from logging import DEBUG, INFO, getLogger
from logging.handlers import TimedRotatingFileHandler
from time import asctime
from traceback import format_exc

from earwigbot.bot import Bot
from earwigbot.wiki.copyvios import globalize
from flask import Flask, g, make_response, request
from flask.ext.mako import MakoTemplates, render_template, TemplateError
from flup.server.fcgi import WSGIServer

from copyvios.api import format_api_error, handle_api_request
from copyvios.checker import do_check
from copyvios.cookies import parse_cookies
from copyvios.misc import cache
from copyvios.settings import process_settings
from copyvios.sites import update_sites

app = Flask(__name__)
MakoTemplates(app)

hand = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
hand.setLevel(DEBUG)
app.logger.addHandler(hand)
app.logger.info(u"Flask server started " + asctime())

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

    getLogger("earwigbot.wiki.cvworker").setLevel(INFO)
    globalize()

@app.before_request
def prepare_request():
    g._db = None
    g.cookies = parse_cookies(
        request.script_root, request.environ.get("HTTP_COOKIE"))
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

@app.route("/")
@catch_errors
def index():
    update_sites()
    query = do_check()
    return render_template("index.mako", query=query, result=query.result)

@app.route("/settings", methods=["GET", "POST"])
@catch_errors
def settings():
    status = process_settings() if request.method == "POST" else None
    update_sites()
    default = cache.bot.wiki.get_site()
    kwargs = {"status": status, "default_lang": default.lang,
              "default_project": default.project}
    return render_template("settings.mako", **kwargs)

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
    WSGIServer(app).run()
