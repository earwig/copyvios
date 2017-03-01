# -*- coding: utf-8  -*-

from __future__ import unicode_literals

from earwigbot.wiki import NS_TEMPLATE

__all__ = ["get_attribution_info"]

ATTRIB_TEMPLATES = {
    "enwiki": {
        "CC-notice", "Cc-notice",
        "Citation-attribution",
        "Free-content attribution", "Open-source attribution",
        "Source-attribution",
    }
}

def get_attribution_info(site, page):
    """Check to see if the given page has some kind of attribution info.

    If yes, return a mwparserfromhell.nodes.Template object for the attribution
    template. If no, return None.
    """
    if site.name not in ATTRIB_TEMPLATES:
        return None

    templates = ATTRIB_TEMPLATES[site.name]
    prefix = site.namespace_id_to_name(NS_TEMPLATE)
    templates |= {prefix + ":" + tmpl for tmpl in templates if ":" not in tmpl}

    for template in page.parse().ifilter_templates():
        if template.name.matches(templates):
            return template
    return None
