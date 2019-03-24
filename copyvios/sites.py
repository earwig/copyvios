# -*- coding: utf-8  -*-

from time import time
from urlparse import urlparse

from earwigbot import exceptions

from .misc import cache

__all__ = ["get_site", "update_sites"]

def get_site(query):
    lang, project, name = query.lang, query.project, query.name
    wiki = cache.bot.wiki
    if project not in [proj[0] for proj in cache.projects]:
        return None
    if project == "wikimedia" and name:  # Special sites:
        try:
            return wiki.get_site(name=name)
        except exceptions.SiteNotFoundError:
            return _add_site(lang, project)
    try:
        return wiki.get_site(lang=lang, project=project)
    except exceptions.SiteNotFoundError:
        return _add_site(lang, project)

def update_sites():
    if time() - cache.last_sites_update > 60 * 60 * 24 * 7:
        cache.langs, cache.projects = _load_sites()
        cache.last_sites_update = time()

def _add_site(lang, project):
    update_sites()
    if not any(project == item[0] for item in cache.projects):
        return None
    if lang != "www" and not any(lang == item[0] for item in cache.langs):
        return None
    try:
        return cache.bot.wiki.add_site(lang=lang, project=project)
    except (exceptions.APIError, exceptions.LoginError):
        return None

def _load_sites():
    site = cache.bot.wiki.get_site()
    matrix = site.api_query(action="sitematrix")["sitematrix"]
    del matrix["count"]
    langs, projects = set(), set()
    for site in matrix.itervalues():
        if isinstance(site, list):  # Special sites
            bad_sites = ["closed", "private", "fishbowl"]
            for special in site:
                if all([key not in special for key in bad_sites]):
                    full = urlparse(special["url"]).netloc
                    if full.count(".") == 1:  # No subdomain, so use "www"
                        lang, project = "www", full.split(".")[0]
                    else:
                        lang, project = full.rsplit(".", 2)[:2]
                    code = u"{0}::{1}".format(lang, special["dbname"])
                    name = special["code"].capitalize()
                    langs.add((code, u"{0} ({1})".format(lang, name)))
                    projects.add((project, project.capitalize()))
        else:
            this = set()
            for web in site["site"]:
                if "closed" in web:
                    continue
                proj = "wikipedia" if web["code"] == u"wiki" else web["code"]
                this.add((proj, proj.capitalize()))
            if this:
                code = site["code"]
                langs.add((code, u"{0} ({1})".format(code, site["name"])))
                projects |= this
    return list(sorted(langs)), list(sorted(projects))
