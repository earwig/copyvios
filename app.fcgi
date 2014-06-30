#! /data/project/copyvios/env/bin/python
# -*- coding: utf-8  -*-

from time import asctime
from logging import DEBUG
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, g, request
from flask.ext.mako import MakoTemplates, render_template, TemplateError
from flup.server.fcgi import WSGIServer

from copyvios.cookies import parse_cookies

app = Flask(__name__)
MakoTemplates(app)

app.logger.setLevel(DEBUG)
app.logger.addHandler(TimedRotatingFileHandler(
    "logs/app.log", when="D", interval=1, backupCount=7))
app.logger.info(u"Flask server started " + asctime())

def debug_exceptions(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TemplateError as exc:
            return "<pre>" + exc.text + "</pre>"
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
@debug_exceptions
def index():
    return render_template("index.mako")

@app.route("/settings", methods=["GET", "POST"])
@debug_exceptions
def settings():
    return render_template("settings.mako")

@app.route("/debug")
@debug_exceptions
def debug():
    return render_template("debug.mako")

if __name__ == '__main__':
    WSGIServer(app).run()
