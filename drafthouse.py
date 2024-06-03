import io
import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Literal, TypedDict
from uuid import uuid4

import click
import lru_cache
import requests


class FeedItem(TypedDict):
    id: str
    url: str
    title: str
    content_html: str


class Feed(TypedDict):
    version: Literal["https://jsonfeed.org/version/1.1"]
    title: str
    home_page_url: str
    feed_url: str
    icon: str
    items: list[FeedItem]


logger = logging.getLogger("drafthouse")

_DRAFTHOUSE_RECOMMENDS_BADGE = (
    '<a href="https://drafthouse.com/movies/drafthouse-recommends">'
    "Drafthouse Recommends</a>"
)

_CACHE_MAX_BYTESIZE = lru_cache.bytesize(mb=1)

_MARKETS = [
    "chicago",
    "los-angeles",
    "nyc",
    "sf",
]


@click.command()
@click.argument("market", type=click.Choice(_MARKETS))
@click.option(
    "-o", "--output-file", type=click.File(mode="w", atomic=True), default="-"
)
@click.option(
    "--cache-path",
    envvar="CACHE_PATH",
    type=click.Path(writable=True, path_type=Path),
    required=True,
)
@click.option("--verbose", "-v", is_flag=True)
def main(
    market: str,
    output_file: io.TextIOWrapper,
    cache_path: Path,
    verbose: bool,
) -> None:
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level)

    cache = lru_cache.open(cache_path, max_bytesize=_CACHE_MAX_BYTESIZE)

    api_url = f"https://drafthouse.com/s/mother/v2/schedule/market/{market}"
    logger.info("Fetch %s", api_url)
    r = requests.get(api_url)
    data = r.json()

    market_obj = data["data"]["market"][0]
    market_slug = market_obj["slug"]
    market_name = market_obj["name"]

    feed: Feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": f"Alamo Drafthouse Cinema | {market_name}",
        "home_page_url": f"https://drafthouse.com/{market_slug}",
        "feed_url": f"https://josh.github.io/alamo-drafthouse-feeds/{market_slug}.json",
        "icon": "https://drafthouse.com/s/res/images/favicons/apple-touch-icon-180x180.png",
        "items": [],
    }

    seen = set()

    presentations = data["data"]["presentations"]
    presentations.sort(key=_sort_presentations)

    for presentation in presentations:
        show = presentation["show"]

        slug = show["slug"]

        if slug in seen:
            continue
        seen.add(slug)

        content_html_parts = []

        image_url = show["landscapeHeroImage"]["uri"]
        if ("w=1920" in image_url) and ("h=1080" in image_url):
            content_html_parts.append(
                f'<img src="{image_url}" '
                'height="1080" width="1920" '
                'style="max-width:564px">'
            )
        else:
            logger.warning("Unexpected image URL: %s", image_url)

        url = f"https://drafthouse.com/{market_slug}/show/{slug}"

        opening_date = _item_opening_date(
            cache,
            url,
            presentation["openingDateClt"],
        )

        if opening_date:
            opening_date_str = opening_date.strftime("%b %-d")
            content_html_parts.append(f"<p>{opening_date_str}</p>")

        if presentation["primaryCollectionSlug"] == "drafthouse-recommends":
            content_html_parts.append(_DRAFTHOUSE_RECOMMENDS_BADGE)

        content_html_parts.append(f"<p>{show['headline']}</p>")
        content_html = "\n".join(content_html_parts)

        feed_id = cache.get_or_load(("id", url), load_value=lambda: str(uuid4()))

        item: FeedItem = {
            "id": feed_id,
            "url": url,
            "title": show["title"],
            "content_html": content_html,
        }
        feed["items"].append(item)

    assert len(feed["items"]) > 0, "No items found"
    cache.close()

    json.dump(feed, output_file, indent=4)


def _item_opening_date(
    cache: lru_cache.LRUCache,
    url: str,
    opening_date_clt: str | None,
) -> date | None:
    key = ("drafthouse_opening_date", url)
    if opening_date := cache.get(key):
        assert isinstance(opening_date, date)
        return opening_date
    elif opening_date_clt:
        opening_date = date.fromisoformat(opening_date_clt)
        cache[key] = opening_date
        return opening_date
    else:
        return None


def _sort_presentations(presentation: dict[str, Any]) -> str:
    event_slug = presentation["slug"]
    show_slug = presentation["show"]["slug"]
    if show_slug == event_slug:
        assert isinstance(show_slug, str)
        return show_slug
    else:
        return f"{show_slug} {event_slug}"


if __name__ == "__main__":
    main()
