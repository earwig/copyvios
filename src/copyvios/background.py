import random
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from json import loads

from earwigbot import exceptions
from flask import g

from .misc import cache

__all__ = ["set_background"]


def _get_commons_site():
    try:
        return cache.bot.wiki.get_site("commonswiki")
    except exceptions.SiteNotFoundError:
        return cache.bot.wiki.add_site(project="wikimedia", lang="commons")


def _load_file(site, filename):
    data = site.api_query(
        action="query",
        prop="imageinfo",
        iiprop="url|size|canonicaltitle",
        titles="File:" + filename,
    )
    res = list(data["query"]["pages"].values())[0]["imageinfo"][0]
    name = res["canonicaltitle"][len("File:") :].replace(" ", "_")
    return name, res["url"], res["descriptionurl"], res["width"], res["height"]


def _get_fresh_potd():
    site = _get_commons_site()
    date = datetime.utcnow().strftime("%Y-%m-%d")
    page = site.get_page("Template:Potd/" + date)
    regex = r"\{\{Potd filename\|(?:1=)?(.*?)\|.*?\}\}"
    filename = re.search(regex, page.get()).group(1)
    return _load_file(site, filename)


def _get_fresh_list():
    site = _get_commons_site()
    page = site.get_page("User:The Earwig/POTD")
    regex = r"\*\*?\s*\[\[:File:(.*?)\]\]"
    filenames = re.findall(regex, page.get())

    # Ensure all workers share the same background each day:
    random.seed(datetime.utcnow().strftime("%Y%m%d"))
    filename = random.choice(filenames)
    return _load_file(site, filename)


def _build_url(screen, filename, url, imgwidth, imgheight):
    width = screen["width"]
    if float(imgwidth) / imgheight > float(screen["width"]) / screen["height"]:
        width = int(float(imgwidth) / imgheight * screen["height"])
    if width >= imgwidth:
        return url
    url = url.replace("/commons/", "/commons/thumb/")
    return "%s/%dpx-%s" % (url, width, urllib.parse.quote(filename.encode("utf8")))


_BACKGROUNDS = {"potd": _get_fresh_potd, "list": _get_fresh_list}


def _get_background(selected):
    if not cache.last_background_updates:
        for key in _BACKGROUNDS:
            cache.last_background_updates[key] = datetime.min

    plus_one = cache.last_background_updates[selected] + timedelta(days=1)
    max_age = datetime(plus_one.year, plus_one.month, plus_one.day)
    if datetime.utcnow() > max_age:
        update_func = _BACKGROUNDS.get(selected, _get_fresh_list)
        cache.background_data[selected] = update_func()
        cache.last_background_updates[selected] = datetime.utcnow().date()
    return cache.background_data[selected]


def set_background(selected):
    if "CopyviosScreenCache" in g.cookies:
        screen_cache = g.cookies["CopyviosScreenCache"].value
        try:
            screen = loads(screen_cache)
            screen = {"width": int(screen["width"]), "height": int(screen["height"])}
            if screen["width"] <= 0 or screen["height"] <= 0:
                raise ValueError()
        except (ValueError, KeyError):
            screen = {"width": 1024, "height": 768}
    else:
        screen = {"width": 1024, "height": 768}

    filename, url, descurl, width, height = _get_background(selected)
    bg_url = _build_url(screen, filename, url, width, height)
    g.descurl = descurl
    return bg_url
