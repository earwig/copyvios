# -*- coding: utf-8  -*-

from os.path import expanduser
from urlparse import parse_qs

from earwigbot.bot import Bot
import oursql

class Query(object):
    def __init__(self, environ):
        self.query = {}
        parsed = parse_qs(environ["QUERY_STRING"])
        for key, value in parsed.iteritems():
            self.query[key] = value[-1].decode("utf8")

    def __getattr__(self, key):
        try:
            return self.query[key]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        if key == "query":
            super(Query, self).__setattr__(key, value)
        else:
            self.query[key] = value


def open_sql_connection(bot, dbname):
    conn_args = bot.config.wiki["_toolserverSQL"][dbname]
    if "read_default_file" not in conn_args and "user" not in conn_args and "passwd" not in conn_args:
        conn_args["read_default_file"] = expanduser("~/.my.cnf")
    if "autoping" not in conn_args:
        conn_args["autoping"] = True
    if "autoreconnect" not in conn_args:
        conn_args["autoreconnect"] = True
    return oursql.connect(**conn_args)

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

def get_bot():
    return Bot(".earwigbot", 100)  # Don't print any logs to the console
