# -*- coding: utf-8  -*-

from os.path import expanduser
from urlparse import parse_qs

from earwigbot.bot import Bot
from flask import request
import oursql

_bot = None
_connections = {}

class Query(object):
    def __init__(self, method="GET"):
        self.query = {}
        if method == "GET":
            parsed = parse_qs(request.environ["QUERY_STRING"])
        elif method == "POST":
            size = int(request.environ.get("CONTENT_LENGTH", 0))
            parsed = parse_qs(request.environ["wsgi.input"].read(size))
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


def get_bot():
    global _bot
    if not _bot:
        _bot = Bot(".earwigbot", 100)  # Don't print any logs to the console
    return _bot

def open_sql_connection(bot, dbname):
    if dbname in _connections:
        return _connections[dbname]
    conn_args = bot.config.wiki["_copyviosSQL"][dbname]
    if "read_default_file" not in conn_args and "user" not in conn_args and "passwd" not in conn_args:
        conn_args["read_default_file"] = expanduser("~/.my.cnf")
    elif "read_default_file" in conn_args:
        default_file = expanduser(conn_args["read_default_file"])
        conn_args["read_default_file"] = default_file
    if "autoping" not in conn_args:
        conn_args["autoping"] = True
    if "autoreconnect" not in conn_args:
        conn_args["autoreconnect"] = True
    conn = oursql.connect(**conn_args)
    _connections[dbname] = conn
    return conn

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
