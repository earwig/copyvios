__all__ = ["cache"]

import os.path
import sqlite3
from dataclasses import dataclass, field
from typing import Any

import sqlalchemy
from earwigbot.bot import Bot


@dataclass(frozen=True, order=True)
class Lang:
    code: str
    name: str


@dataclass(frozen=True, order=True)
class Project:
    code: str
    name: str


@dataclass
class AppCache:
    bot: Bot
    engine: sqlalchemy.Engine
    langs: list[Lang] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)


@sqlalchemy.event.listens_for(sqlalchemy.Engine, "connect")
def setup_connection(dbapi_connection: Any, connection_record: Any) -> None:
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


def _get_engine(bot: Bot) -> sqlalchemy.Engine:
    args = bot.config.wiki.get("copyvios", {}).get("sql", {}).copy()
    engine_name = args.pop("engine", "mysql").lower()

    if engine_name == "mysql":
        url_object = sqlalchemy.URL.create(
            "mysql+pymysql",
            host=args["host"],
            database=args["db"],
            query={
                "charset": "utf8mb4",
                "read_default_file": os.path.expanduser("~/.my.cnf"),
            },
        )
        return sqlalchemy.create_engine(url_object, pool_pre_ping=True)

    if engine_name == "sqlite":
        dbpath = os.path.join(bot.config.root_dir, "copyvios.db")
        return sqlalchemy.create_engine("sqlite:///" + dbpath)

    raise ValueError(f"Unknown engine: {engine_name}")


def _make_cache() -> AppCache:
    bot = Bot(".earwigbot", 100)
    engine = _get_engine(bot)
    return AppCache(bot=bot, engine=engine)


# Singleton
cache = _make_cache()
