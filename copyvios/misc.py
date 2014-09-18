# -*- coding: utf-8  -*-

from os.path import expanduser

from flask import g, request
import oursql
from sqlalchemy.pool import manage

oursql = manage(oursql)

__all__ = ["Query", "get_db", "httpsfix", "urlstrip"]

class Query(object):
    def __init__(self, method="GET"):
        self.query = {}
        data = request.form if method == "POST" else request.args
        for key in data:
            self.query[key] = data.getlist(key)[-1]

    def __getattr__(self, key):
        return self.query.get(key)

    def __setattr__(self, key, value):
        if key == "query":
            super(Query, self).__setattr__(key, value)
        else:
            self.query[key] = value


def get_db():
    if not g.db:
        args = g.bot.config.wiki["_copyviosSQL"]
        args["read_default_file"] = expanduser("~/.my.cnf")
        args["autoping"] = True
        args["autoreconnect"] = True
        g.db = oursql.connect(**args)
    return g.db

def httpsfix(context, url):
    if url.startswith("http://"):
        url = url[len("http:"):]
    return url

def urlstrip(context, url):
    if url.startswith("http://"):
        url = url[7:]
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("www."):
        url = url[4:]
    if url.endswith("/"):
        url = url[:-1]
    return url
