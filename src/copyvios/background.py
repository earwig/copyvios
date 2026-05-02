__all__ = ["get_background"]

import functools
import json
import logging
import random
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Self

from earwigbot import exceptions
from earwigbot.wiki import Site

from .cache import cache
from .cookies import get_cookies

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BackgroundInfo:
    filename: str


@dataclass(frozen=True)
class BackgroundURLs:
    url: str
    descurl: str


@dataclass(frozen=True)
class ScreenInfo:
    width: int = 1024
    height: int = 768

    @classmethod
    def from_cookie(cls, value: str) -> Self:
        try:
            screen = json.loads(value)
            screen = cls(width=int(screen["width"]), height=int(screen["height"]))
            if screen.width <= 0 or screen.height <= 0:
                raise ValueError()
        except (ValueError, KeyError):
            screen = cls()
        return screen


def _get_commons_site() -> Site:
    try:
        return cache.bot.wiki.get_site("commonswiki")
    except exceptions.SiteNotFoundError:
        return cache.bot.wiki.add_site(project="wikimedia", lang="commons")


def _get_fresh_from_potd() -> BackgroundInfo | None:
    site = _get_commons_site()
    date = datetime.now(UTC).strftime("%Y-%m-%d")
    page = site.get_page(f"Template:Potd/{date}")
    filename = None
    try:
        code = page.parse()
        for tmpl in code.ifilter_templates(
            matches=lambda tmpl: tmpl.name.matches("Potd filename")
        ):
            filename = tmpl.get(1).value.strip_code().strip()
            break
    except exceptions.EarwigBotError:
        logger.exception(f"Failed to load today's POTD from {page.title!r}")
        return None
    if not filename:
        logger.exception(f"Failed to extract POTD from {page.title!r}")
        return None
    return BackgroundInfo(filename)


def _get_fresh_from_list() -> BackgroundInfo | None:
    site = _get_commons_site()
    page = site.get_page("User:The Earwig/POTD")
    regex = r"\*\*?\s*\[\[:File:(.*?)\]\]"
    try:
        filenames = re.findall(regex, page.get())
    except exceptions.EarwigBotError:
        logger.exception(f"Failed to load images from {page.title!r}")
        return None

    # Ensure all workers share the same background each day
    rand = random.Random()
    rand.seed(datetime.now(UTC).strftime("%Y%m%d"))
    try:
        filename = rand.choice(filenames)
    except IndexError:
        logger.exception(f"Failed to find any images on {page.title!r}")
        return None
    return BackgroundInfo(filename)


_BACKGROUNDS = {
    "potd": _get_fresh_from_potd,
    "list": _get_fresh_from_list,
}

_BACKGROUND_INFO_CACHE: dict[str, BackgroundInfo | None] = {}
_LAST_BACKGROUND_UPDATES: dict[str, date] = {
    key: datetime.min.date() for key in _BACKGROUNDS
}


def _get_background_info(selected: str) -> BackgroundInfo | None:
    next_day = _LAST_BACKGROUND_UPDATES[selected] + timedelta(days=1)
    max_age = datetime(next_day.year, next_day.month, next_day.day, tzinfo=UTC)
    if datetime.now(UTC) > max_age:
        update_func = _BACKGROUNDS.get(selected, _get_fresh_from_list)
        _BACKGROUND_INFO_CACHE[selected] = update_func()
        _LAST_BACKGROUND_UPDATES[selected] = datetime.now(UTC).date()
    return _BACKGROUND_INFO_CACHE[selected]


@functools.lru_cache(maxsize=256)
def _get_background_urls(
    background: BackgroundInfo, screen_width: int
) -> BackgroundURLs | None:
    site = _get_commons_site()
    prefix = "File:"
    try:
        data = site.api_query(
            action="query",
            prop="imageinfo",
            iiprop="url|canonicaltitle",
            iiurlwidth=screen_width,
            titles=prefix + background.filename,
        )
        res = list(data["query"]["pages"].values())[0]["imageinfo"][0]
        name = res["canonicaltitle"]
        assert isinstance(name, str), name
        url = res["thumburl"]
        descurl = res["descriptionurl"]
    except Exception:
        logger.exception(
            f"Failed to get info for file {prefix + background.filename!r}"
        )
        return None
    name = name.removeprefix(prefix).replace(" ", "_")
    return BackgroundURLs(url=url, descurl=descurl)


def get_background(selected: str) -> tuple[str | None, str | None]:
    if selected == "plain":
        return None, None

    cookies = get_cookies()
    if "CopyviosScreenCache" in cookies:
        cookie = cookies["CopyviosScreenCache"].value
        screen = ScreenInfo.from_cookie(cookie)
    else:
        screen = ScreenInfo()

    bg_info = _get_background_info(selected)
    if bg_info is not None:
        bg_urls = _get_background_urls(bg_info, screen.width)
        if bg_urls is not None:
            return bg_urls.url, bg_urls.descurl
    return None, None
