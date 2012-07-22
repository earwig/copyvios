# -*- coding: utf-8  -*-

from os.path import expanduser

import oursql

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
