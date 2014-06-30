#! /data/project/copyvios/env/bin/python
# -*- coding: utf-8  -*-

from functools import wraps
from logging import DEBUG
from logging.handlers import TimedRotatingFileHandler
from time import asctime
from traceback import format_exc

from flask import Flask, g, request
from flask.ext.mako import MakoTemplates, render_template, TemplateError
from flup.server.fcgi import WSGIServer

from copyvios.cookies import parse_cookies
from copyvios.misc import get_bot
from copyvios.settings import process_settings
from copyvios.sites import get_sites

app = Flask(__name__)
MakoTemplates(app)

app.logger.setLevel(DEBUG)
app.logger.addHandler(TimedRotatingFileHandler(
    "logs/app.log", when="D", interval=1, backupCount=7))
app.logger.info(u"Flask server started " + asctime())

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
def prepare_cookies():
    cookie_string = request.environ.get("HTTP_COOKIE")
    g.cookies = parse_cookies(request.script_root, cookie_string)
    g.new_cookies = []

@app.after_request
def add_new_cookies(response):
    if g.new_cookies:
        if "Set-Cookie" in response.headers:
            g.new_cookies.insert(0, response.headers["Set-Cookie"])
        response.headers["Set-Cookie"] = "; ".join(g.new_cookies)
    return response

@app.after_request
def write_access_log(response):
    msg = u"%s %s -> %s"
    app.logger.debug(msg, asctime(), request.path, response.status_code)
    return response

@app.route("/")
@catch_errors
def index():
    return render_template("index.mako")

@app.route("/settings", methods=["GET", "POST"])
@catch_errors
def settings():
    status = process_settings() if request.method == "POST" else None
    bot = get_bot()
    langs, projects = get_sites(bot)
    default = bot.wiki.get_site()
    kwargs = {"status": status, "langs": langs, "projects": projects,
              "default_lang": default.lang, "default_project": default.project}
    return render_template("settings.mako", **kwargs)

@app.route("/debug")
@catch_errors
def debug():
    return render_template("debug.mako")

if __name__ == '__main__':
    WSGIServer(app).run()
