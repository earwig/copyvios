#! /data/project/copyvios/env/bin/python
# -*- coding: utf-8  -*-

from functools import wraps
from logging import DEBUG
from logging.handlers import TimedRotatingFileHandler
from time import asctime
from traceback import format_exc

from earwigbot.bot import Bot
from flask import Flask, g, request
from flask.ext.mako import MakoTemplates, render_template, TemplateError
from flup.server.fcgi import WSGIServer

from copyvios.checker import do_check
from copyvios.cookies import parse_cookies
from copyvios.settings import process_settings
from copyvios.sites import get_sites

app = Flask(__name__)
MakoTemplates(app)

app.logger.setLevel(DEBUG)
app.logger.addHandler(TimedRotatingFileHandler(
    "logs/app.log", when="midnight", backupCount=7))
app.logger.info(u"Flask server started " + asctime())

bot = Bot(".earwigbot", 0)

def catch_errors(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TemplateError as exc:
            return render_template("error.mako", traceback=exc.text)
        except Exception:
            return render_template("error.mako", traceback=format_exc())
    return inner

@app.before_request
def prepare_request():
    g.bot = bot
    g.globals_db = g.cache_db = None
    g.cookies = parse_cookies(request.script_root,
                              request.environ.get("HTTP_COOKIE"))
    g.new_cookies = []

@app.after_request
def add_new_cookies(response):
    for cookie in g.new_cookies:
        response.headers.add("Set-Cookie", cookie)
    return response

@app.after_request
def write_access_log(response):
    msg = u"%s %s -> %s"
    app.logger.debug(msg, asctime(), request.path, response.status_code)
    return response

@app.teardown_appcontext
def close_databases(error):
    if g.globals_db:
        g.globals_db.close()
    if g.cache_db:
        g.cache_db.close()

@app.route("/")
@catch_errors
def index():
    query = do_check()
    return render_template("index.mako", query=query, result=query.result)

@app.route("/settings", methods=["GET", "POST"])
@catch_errors
def settings():
    status = process_settings() if request.method == "POST" else None
    langs, projects = get_sites()
    default = bot.wiki.get_site()
    kwargs = {"status": status, "langs": langs, "projects": projects,
              "default_lang": default.lang, "default_project": default.project}
    return render_template("settings.mako", **kwargs)

if __name__ == '__main__':
    WSGIServer(app).run()
