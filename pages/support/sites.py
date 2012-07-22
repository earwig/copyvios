# -*- coding: utf-8  -*-

from time import time
from urlparse import urlparse

from earwigbot import exceptions

def get_site(bot, lang, project, name, all_projects):
    if project not in [proj[0] for proj in all_projects]:
        return None
    if project == "wikimedia" and name:  # Special sites:
        try:
            return bot.wiki.get_site(name=name)
        except exceptions.SiteNotFoundError:
            try:
                return bot.wiki.add_site(lang=lang, project=project)
            except (exceptions.APIError, exceptions.LoginError):
                return None
    try:
        return bot.wiki.get_site(lang=lang, project=project)
    except exceptions.SiteNotFoundError:
        try:
            return bot.wiki.add_site(lang=lang, project=project)
        except (exceptions.APIError, exceptions.LoginError):
            return None

def get_sites(bot):
    max_staleness = 60 * 60 * 24 * 7
    conn = open_sql_connection(bot, "globals")
    query1 = "SELECT update_time FROM updates WHERE update_service = ?"
    query2 = "SELECT lang_code, lang_name FROM language"
    query3 = "SELECT project_code, project_name FROM project"
    with conn.cursor() as cursor:
        cursor.execute(query1, ("sites",))
        try:
            time_since_update = int(time() - cursor.fetchall()[0][0])
        except IndexError:
            time_since_update = time()
        if time_since_update > max_staleness:
            update_sites(bot.wiki.get_site(), cursor)
        cursor.execute(query2)
        langs = []
        for code, name in cursor.fetchall():
            if "\U" in name:
                name = name.decode("unicode_escape")
            langs.append((code, name))
        cursor.execute(query3)
        projects = cursor.fetchall()
    return langs, projects

def update_sites(site, cursor):
    matrix = site.api_query(action="sitematrix")["sitematrix"]
    del matrix["count"]
    languages, projects = set(), set()
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
                    languages.add((code, u"{0} ({1})".format(lang, name)))
                    projects.add((project, project.capitalize()))
            continue
        this = set()
        for web in site["site"]:
            if "closed" in web:
                continue
            project = "wikipedia" if web["code"] == u"wiki" else web["code"]
            this.add((project, project.capitalize()))
        if this:
            code = site["code"]
            if "\U" in site["name"].encode("unicode_escape"):
                name = site["name"].encode("unicode_escape")
            else:
                name = site["name"]
            languages.add((code, u"{0} ({1})".format(code, name)))
            projects |= this
    save_site_updates(cursor, languages, projects)

def save_site_updates(cursor, languages, projects):
    query1 = "SELECT lang_code, lang_name FROM language"
    query2 = "DELETE FROM language WHERE lang_code = ? AND lang_name = ?"
    query3 = "INSERT INTO language VALUES (?, ?)"
    query4 = "SELECT project_code, project_name FROM project"
    query5 = "DELETE FROM project WHERE project_code = ? AND project_name = ?"
    query6 = "INSERT INTO project VALUES (?, ?)"
    query7 = "SELECT 1 FROM updates WHERE update_service = ?"
    query8 = "UPDATE updates SET update_time = ? WHERE update_service = ?"
    query9 = "INSERT INTO updates VALUES (?, ?)"
    synchronize_sites_with_db(cursor, languages, query1, query2, query3)
    synchronize_sites_with_db(cursor, projects, query4, query5, query6)
    cursor.execute(query7, ("sites",))
    if cursor.fetchall():
        cursor.execute(query8, (time(), "sites"))
    else:
        cursor.execute(query9, ("sites", time()))

def synchronize_sites_with_db(cursor, updates, q_list, q_rmv, q_update):
    removals = []
    cursor.execute(q_list)
    for site in cursor:
        updates.remove(site) if site in updates else removals.append(site)
    cursor.executemany(q_rmv, removals)
    cursor.executemany(q_update, updates)
