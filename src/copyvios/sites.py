__all__ = ["get_site", "update_sites"]

import urllib.parse
from datetime import UTC, datetime, timedelta

from earwigbot import exceptions
from earwigbot.wiki import Site
from flask import g

from .cache import Lang, Project, cache
from .query import CheckQuery

_LAST_SITES_UPDATE = datetime.min.replace(tzinfo=UTC)


def _get_site(query: CheckQuery) -> Site | None:
    if not any(proj.code == query.project for proj in cache.projects):
        return None
    try:
        if query.project == "wikimedia" and query.name:  # Special sites
            return cache.bot.wiki.get_site(name=query.name)
        else:
            return cache.bot.wiki.get_site(lang=query.lang, project=query.project)
    except exceptions.SiteNotFoundError:
        assert query.lang and query.project, (query.lang, query.project)
        return _add_site(query.lang, query.project)


def get_site(query: CheckQuery | None = None) -> Site | None:
    if "site" not in g:
        assert query is not None, "get_site() called with no cached site nor query"
        g.site = _get_site(query)
    assert g.site is None or isinstance(g.site, Site), g.site
    return g.site


def update_sites() -> None:
    global _LAST_SITES_UPDATE

    now = datetime.now(UTC)
    if now - _LAST_SITES_UPDATE > timedelta(days=1):
        cache.langs, cache.projects = _load_sites()
        _LAST_SITES_UPDATE = now


def _add_site(lang: str, project: str) -> Site | None:
    update_sites()
    if not any(project == proj.code for proj in cache.projects):
        return None
    if lang != "www" and not any(lang == item.code for item in cache.langs):
        return None
    try:
        return cache.bot.wiki.add_site(lang=lang, project=project)
    except (exceptions.APIError, exceptions.LoginError):
        return None


def _load_sites() -> tuple[list[Lang], list[Project]]:
    site = cache.bot.wiki.get_site()
    matrix = site.api_query(action="sitematrix")["sitematrix"]
    del matrix["count"]
    langs: set[Lang] = set()
    projects: set[Project] = set()

    for site in matrix.values():
        if isinstance(site, list):  # Special sites
            bad_sites = ["closed", "private", "fishbowl"]
            for special in site:
                if any(key in special for key in bad_sites):
                    continue
                full = urllib.parse.urlparse(special["url"]).netloc
                if full.count(".") == 1:  # No subdomain, so use "www"
                    lang, project = "www", full.split(".")[0]
                else:
                    lang, project = full.rsplit(".", 2)[:2]
                langcode = f"{lang}::{special['dbname']}"
                langname = special["code"].capitalize()
                langs.add(Lang(langcode, f"{lang} ({langname})"))
                projects.add(Project(project, project.capitalize()))
        else:
            this: set[Project] = set()
            for web in site["site"]:
                if "closed" in web:
                    continue
                proj = "wikipedia" if web["code"] == "wiki" else web["code"]
                this.add(Project(proj, proj.capitalize()))
            if this:
                code = site["code"]
                langs.add(Lang(code, f"{code} ({site['name']})"))
                projects |= this

    return sorted(langs), sorted(projects)
