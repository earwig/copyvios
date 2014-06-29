#! /data/project/copyvios/env/bin/python
# -*- coding: utf-8  -*-

from time import asctime
from logging import DEBUG, FileHandler

from flask import Flask, request
from flask.ext.mako import render_template
from flup.server.fcgi import WSGIServer

app = Flask(__name__, static_folder="static", static_url_path="/copyvios/static")

logger = FileHandler("error.log")
app.logger.setLevel(DEBUG)
app.logger.addHandler(logger)
app.logger.info(u"Flask server started " + asctime())

@app.after_request
def write_access_log(response):
    app.logger.debug(u"%s %s -> %s" % (asctime(), request.path, response.status_code))
    return response

@app.route("/copyvios")
def index():
    return render_template("index.mako")

@app.route("/copyvios/settings")
def settings():
    return render_template("settings.mako")

@app.route("/copyvios/debug")
def debug():
    return render_template("debug.mako")

if __name__ == '__main__':
    WSGIServer(app).run()
