# -*- coding: utf-8  -*-

from os.path import expanduser
from urlparse import parse_qs

from flask import g, request
import oursql
from sqlalchemy.pool import manage

oursql = manage(oursql)

__all__ = ["Query", "get_globals_db", "get_cache_db", "httpsfix", "urlstrip"]

class Query(object):
    def __init__(self, method="GET"):
        self.query = {}
        if method == "GET":
            parsed = parse_qs(request.environ["QUERY_STRING"],
                              keep_blank_values=True)
        elif method == "POST":
            size = int(request.environ.get("CONTENT_LENGTH", 0))
            parsed = parse_qs(request.environ["wsgi.input"].read(size),
                              keep_blank_values=True)
        else:
            parsed = {}
        for key, value in parsed.iteritems():
            try:
                self.query[key] = value[-1].decode("utf8")
            except UnicodeDecodeError:
                pass

    def __getattr__(self, key):
        return self.query.get(key)

    def __setattr__(self, key, value):
        if key == "query":
            super(Query, self).__setattr__(key, value)
        else:
            self.query[key] = value


def _connect_db(name):
    args = g.bot.config.wiki["_copyviosSQL"][name]
    args["read_default_file"] = expanduser("~/.my.cnf")
    args["autoping"] = True
    args["autoreconnect"] = True
    return oursql.connect(**args)

def get_globals_db():
    if not g.globals_db:
        g.globals_db = _connect_db("globals")
    return g.globals_db

def get_cache_db():
    if not g.cache_db:
        g.cache_db = _connect_db("cache")
    return g.cache_db

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
