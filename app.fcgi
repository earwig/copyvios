#! /data/project/copyvios/env/bin/python
# -*- coding: utf-8  -*-

from time import asctime
from logging import DEBUG
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, request
from flask.ext.mako import MakoTemplates, render_template
from flup.server.fcgi import WSGIServer

app = Flask(__name__)
MakoTemplates(app)

app.logger.setLevel(DEBUG)
app.logger.addHandler(TimedRotatingFileHandler("logs/app.log", when="D",
                                               interval=1, backupCount=7))
app.logger.info(u"Flask server started " + asctime())

@app.after_request
def write_access_log(response):
    msg = u"%s %s -> %s"
    app.logger.debug(msg, asctime(), request.path, response.status_code)
    return response

@app.route("/")
def index():
    return render_template("index.mako")

@app.route("/settings")
def settings():
    return render_template("settings.mako")

@app.route("/debug")
def debug():
    return render_template("debug.mako")

if __name__ == '__main__':
    WSGIServer(app).run()
