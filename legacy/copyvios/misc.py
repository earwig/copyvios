# -*- coding: utf-8  -*-

from contextlib import contextmanager
import datetime
from os.path import expanduser, join

import apsw
from flask import g, request
import oursql
from sqlalchemy.pool import manage

oursql = manage(oursql)

__all__ = ["Query", "cache", "get_db", "get_notice", "httpsfix", "urlstrip"]

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


class _AppCache(object):
    def __init__(self):
        super(_AppCache, self).__setattr__("_data", {})

    def __getattr__(self, key):
        return self._data[key]

    def __setattr__(self, key, value):
        self._data[key] = value


cache = _AppCache()

def _connect_to_db(engine, args):
    if engine == "mysql":
        args["read_default_file"] = expanduser("~/.my.cnf")
        args["autoping"] = True
        args["autoreconnect"] = True
        return oursql.connect(**args)
    if engine == "sqlite":
        dbpath = join(cache.bot.config.root_dir, "copyvios.db")
        conn = apsw.Connection(dbpath)
        conn.cursor().execute("PRAGMA foreign_keys = ON")
        return conn
    raise ValueError("Unknown engine: %s" % engine)

def get_db():
    if not g._db:
        args = cache.bot.config.wiki["_copyviosSQL"].copy()
        g._engine = engine = args.pop("engine", "mysql").lower()
        g._db = _connect_to_db(engine, args)
    return g._db

@contextmanager
def get_cursor(conn):
    if g._engine == "mysql":
        with conn.cursor() as cursor:
            yield cursor
    elif g._engine == "sqlite":
        with conn:
            yield conn.cursor()
    else:
        raise ValueError("Unknown engine: %s" % g._engine)

def get_sql_error():
    if g._engine == "mysql":
        return oursql.Error
    if g._engine == "sqlite":
        return apsw.Error
    raise ValueError("Unknown engine: %s" % g._engine)

def sql_dialect(mysql, sqlite):
    if g._engine == "mysql":
        return mysql
    if g._engine == "sqlite":
        return sqlite
    raise ValueError("Unknown engine: %s" % g._engine)

def get_notice():
    try:
        with open(expanduser("~/copyvios_notice.html")) as fp:
            lines = fp.read().decode("utf8").strip().splitlines()
            if lines[0] == "<!-- active -->":
                return "\n".join(lines[1:])
            return None
    except IOError:
        return None

def httpsfix(context, url):
    if url.startswith("http://"):
        url = url[len("http:"):]
    return url

def parse_wiki_timestamp(timestamp):
    return datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S')

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
