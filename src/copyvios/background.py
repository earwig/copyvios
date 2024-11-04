__all__ = ["get_background"]

import json
import logging
import random
import re
import urllib.error
import urllib.parse
import urllib.request
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
    url: str
    descurl: str
    width: int
    height: int


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


def _load_file(site: Site, filename: str) -> BackgroundInfo | None:
    prefix = "File:"
    try:
        data = site.api_query(
            action="query",
            prop="imageinfo",
            iiprop="url|size|canonicaltitle",
            titles=prefix + filename,
        )
        res = list(data["query"]["pages"].values())[0]["imageinfo"][0]
        name = res["canonicaltitle"]
        assert isinstance(name, str), name
    except Exception:
        logger.exception(f"Failed to get info for file {prefix + filename!r}")
        return None
    name = name.removeprefix(prefix).replace(" ", "_")
    return BackgroundInfo(
        name, res["url"], res["descriptionurl"], res["width"], res["height"]
    )


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
    return _load_file(site, filename)


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
    return _load_file(site, filename)


def _build_url(screen: ScreenInfo, background: BackgroundInfo) -> str:
    width = screen.width
    if background.width / background.height > screen.width / screen.height:
        width = int(background.width / background.height * screen.height)
    if width >= background.width:
        return background.url
    url = background.url.replace("/commons/", "/commons/thumb/")
    return f"{url}/{width}px-{urllib.parse.quote(background.filename)}"


_BACKGROUNDS = {
    "potd": _get_fresh_from_potd,
    "list": _get_fresh_from_list,
}

_BACKGROUND_CACHE: dict[str, BackgroundInfo | None] = {}
_LAST_BACKGROUND_UPDATES: dict[str, date] = {
    key: datetime.min.date() for key in _BACKGROUNDS
}


def _get_background(selected: str) -> BackgroundInfo | None:
    next_day = _LAST_BACKGROUND_UPDATES[selected] + timedelta(days=1)
    max_age = datetime(next_day.year, next_day.month, next_day.day, tzinfo=UTC)
    if datetime.now(UTC) > max_age:
        update_func = _BACKGROUNDS.get(selected, _get_fresh_from_list)
        _BACKGROUND_CACHE[selected] = update_func()
        _LAST_BACKGROUND_UPDATES[selected] = datetime.now(UTC).date()
    return _BACKGROUND_CACHE[selected]


def get_background(selected: str) -> tuple[str | None, str | None]:
    if selected == "plain":
        return None, None

    cookies = get_cookies()
    if "CopyviosScreenCache" in cookies:
        cookie = cookies["CopyviosScreenCache"].value
        screen = ScreenInfo.from_cookie(cookie)
    else:
        screen = ScreenInfo()

    background = _get_background(selected)
    if background:
        bg_url = _build_url(screen, background)
        return bg_url, background.descurl
    else:
        return None, None
