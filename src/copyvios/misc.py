__all__ = [
    "get_notice",
    "get_sql_error",
    "httpsfix",
    "parse_wiki_timestamp",
    "sql_dialect",
    "urlstrip",
]

import datetime
import os
import sqlite3
from typing import TypeVar

import pymysql

from .cache import cache

T = TypeVar("T")


def get_sql_error() -> type[Exception]:
    match cache.engine.dialect.name:
        case "mysql":
            return pymysql.Error
        case "sqlite":
            return sqlite3.Error
        case dialect:
            raise ValueError(f"Unknown engine: {dialect}")


def sql_dialect(mysql: T, sqlite: T) -> T:
    match cache.engine.dialect.name:
        case "mysql":
            return mysql
        case "sqlite":
            return sqlite
        case dialect:
            raise ValueError(f"Unknown engine: {dialect}")


def get_notice() -> str | None:
    try:
        with open(os.path.expanduser("~/copyvios_notice.html")) as fp:
            lines = fp.read().strip().splitlines()
            if lines and lines[0] == "<!-- active -->":
                return "\n".join(lines[1:])
            return None
    except OSError:
        return None


def httpsfix(context, url: str) -> str:
    if url.startswith("http://"):
        url = url[len("http:") :]
    return url


def parse_wiki_timestamp(timestamp: str) -> datetime.datetime:
    return datetime.datetime.strptime(timestamp, "%Y%m%d%H%M%S")


def urlstrip(context, url: str) -> str:
    if url.startswith("http://"):
        url = url[7:]
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("www."):
        url = url[4:]
    if url.endswith("/"):
        url = url[:-1]
    return url
