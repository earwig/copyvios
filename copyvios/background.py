# -*- coding: utf-8  -*-

from datetime import datetime, timedelta
from json import loads
import random
import re
from time import time

from earwigbot import exceptions

from .misc import get_bot, open_sql_connection

_descurl = None

def set_background(context, cookies, selected):
    global _descurl
    conn = open_sql_connection(get_bot(), "globals")
    if "CopyviosScreenCache" in cookies:
        cache = cookies["CopyviosScreenCache"].value
        try:
            screen = loads(cache)
            int(screen["width"])
            int(screen["height"])
        except (ValueError, KeyError):
            screen = {"width": 1024, "height": 768}
    else:
        screen = {"width": 1024, "height": 768}

    if selected == "potd":
        info = _update_url(conn, "background_potd", 1, _get_fresh_potd)
    else:
        info = _update_url(conn, "background_list", 2, _get_fresh_list)
    filename, url, descurl, width, height = info
    bg_url = _build_url(screen, filename, url, width, height)
    _descurl = descurl
    return bg_url

def get_desc_url(context):
    return _descurl

def _update_url(conn, service, bg_id, callback):
    query1 = "SELECT update_time FROM updates WHERE update_service = ?"
    query2 = "SELECT 1 FROM background WHERE background_id = ?"
    query3 = "DELETE FROM background WHERE background_id = ?"
    query4 = "INSERT INTO background VALUES (?, ?, ?, ?, ?, ?)"
    query5 = "SELECT 1 FROM updates WHERE update_service = ?"
    query6 = "UPDATE updates SET update_time = ? WHERE update_service = ?"
    query7 = "INSERT INTO updates VALUES (?, ?)"
    query8 = "SELECT * FROM background WHERE background_id = ?"
    with conn.cursor() as cursor:
        cursor.execute(query1, (service,))
        try:
            update_time = datetime.utcfromtimestamp(cursor.fetchall()[0][0])
        except IndexError:
            update_time = datetime.min
        plus_one = update_time + timedelta(days=1)
        max_age = datetime(plus_one.year, plus_one.month, plus_one.day)
        if datetime.utcnow() > max_age:
            filename, url, descurl, width, height = callback()
            cursor.execute(query2, (bg_id,))
            if cursor.fetchall():
                cursor.execute(query3, (bg_id,))
            cursor.execute(query4, (bg_id, filename, url, descurl, width,
                                    height))
            cursor.execute(query5, (service,))
            if cursor.fetchall():
                cursor.execute(query6, (time(), service))
            else:
                cursor.execute(query7, (service, time()))
        else:
            cursor.execute(query8, (bg_id,))
            filename, url, descurl, width, height = cursor.fetchone()[1:]
    return filename, url, descurl, width, height

def _get_fresh_potd():
    site = _get_site()
    date = datetime.utcnow().strftime("%Y-%m-%d")
    page = site.get_page("Template:Potd/" + date)
    regex = ur"\{\{Potd filename\|(?:1=)?(.*?)\|.*?\}\}"
    filename = re.search(regex, page.get()).group(1)
    return _load_file(site, filename)

def _get_fresh_list():
    site = _get_site()
    page = site.get_page("User:The Earwig/POTD")
    regex = ur"\*\*?\s*\[\[:File:(.*?)\]\]"
    filenames = re.findall(regex, page.get())
    filename = random.choice(filenames)
    return _load_file(site, filename)

def _load_file(site, filename):
    res = site.api_query(action="query", prop="imageinfo", iiprop="url|size",
                         titles="File:" + filename)
    data = res["query"]["pages"].values()[0]["imageinfo"][0]
    url = data["url"]
    descurl = data["descriptionurl"]
    width = data["width"]
    height = data["height"]
    return filename.replace(" ", "_"), url, descurl, width, height

def _get_site():
    bot = get_bot()
    try:
        return bot.wiki.get_site("commonswiki")
    except exceptions.SiteNotFoundError:
        return bot.wiki.add_site(project="wikimedia", lang="commons")

def _build_url(screen, filename, url, imgwidth, imgheight):
    width = screen["width"]
    if float(imgwidth) / imgheight > float(screen["width"]) / screen["height"]:
        width = int(float(imgwidth) / imgheight * screen["height"])
    if width >= imgwidth:
        return url
    url = url.replace("/commons/", "/commons/thumb/")
    return url + "/" + str(width) + "px-" + filename
