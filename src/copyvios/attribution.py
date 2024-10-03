__all__ = ["get_attribution_info"]

from earwigbot.wiki import NS_TEMPLATE, Page, Site

ATTRIB_TEMPLATES = {
    "enwiki": {
        "CC-notice",
        "Cc-notice",
        "Citation-attribution",
        "Free-content attribution",
        "Open-source attribution",
        "Source-attribution",
    }
}


def get_attribution_info(site: Site, page: Page) -> tuple[str, str] | None:
    """
    Check to see if the given page has some kind of attribution info.

    Return a tuple of (attribution template name, template URL) or None if no template.
    """
    if site.name not in ATTRIB_TEMPLATES:
        return None

    base = ATTRIB_TEMPLATES[site.name]
    prefix = site.namespace_id_to_name(NS_TEMPLATE)
    templates = base | {prefix + ":" + tpl for tpl in base if ":" not in tpl}

    for template in page.parse().ifilter_templates():
        if template.name.matches(templates):
            name = str(template.name).strip()
            title = name if ":" in name else prefix + ":" + name
            return name, site.get_page(title).url

    return None
