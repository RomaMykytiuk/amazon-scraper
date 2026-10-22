
from pathlib import Path
from urllib.parse import urlparse
import hashlib

import httpx
from bs4 import BeautifulSoup

from parse_categories import parse_categories

BASE_DIR = Path(__file__).resolve().parent

CACHE_DIR = BASE_DIR / "cache_pages"
CACHE_DIR.mkdir(exist_ok=True)

LOCAL_PAGES = {
    "": "amazon_trending.html",
    "electronics": "amazon_electronics.html",
    "electronics/172541": "amazon_headphones.html"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}


def read_html(filename):
    path = BASE_DIR / filename

    if not path.is_file():
        return None

    return path.read_text(
        encoding="utf-8",
        errors="replace"
    )


def get_root_categories():
    html = read_html("amazon_trending.html")

    if html is None:
        return []

    return parse_categories(html)


def get_known_categories():
    known = {}

    paths = []

    for filename in LOCAL_PAGES.values():
        path = BASE_DIR / filename

        if path.is_file():
            paths.append(path)

    paths.extend(CACHE_DIR.glob("*.html"))

    for path in paths:
        html = read_html(path) if not path.is_absolute() else path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        if html is None:
            continue

        for category in parse_categories(html):
            known[category["id"]] = category

    return known


def get_category_name(category_id):
    if not category_id:
        return "Trending Products"

    categories = get_known_categories()

    if category_id in categories:
        return categories[category_id]["name"]

    return category_id


def get_cache_path(category_id):
    filename = hashlib.sha256(
        category_id.encode("utf-8")
    ).hexdigest() + ".html"

    return CACHE_DIR / filename


def get_category_info(category_id):
    html = None

    if category_id in LOCAL_PAGES:
        html = read_html(LOCAL_PAGES[category_id])

    if html is None:
        cache_file = get_cache_path(category_id)

        if cache_file.exists():
            html = cache_file.read_text(
                encoding="utf-8",
                errors="replace"
            )

    if html is None:
        categories = get_known_categories()
        category = categories.get(category_id)

        if category is None:
            return {
                "html": None,
                "subcategories": [],
                "error": "Категорію не знайдено."
            }

        url = category["url"]
        parsed = urlparse(url)

        if (
            parsed.scheme != "https"
            or parsed.hostname not in (
                "amazon.com",
                "www.amazon.com"
            )
            or "/zgbs/" not in parsed.path
        ):
            return {
                "html": None,
                "subcategories": [],
                "error": "Некоректне посилання Amazon."
            }

        try:
            response = httpx.get(
                url,
                headers=HEADERS,
                timeout=20,
                follow_redirects=False
            )

            if response.status_code != 200:
                return {
                    "html": None,
                    "subcategories": [],
                    "error": (
                        f"Amazon повернув HTTP "
                        f"{response.status_code}"
                    )
                }

            if len(response.content) > 5_000_000:
                return {
                    "html": None,
                    "subcategories": [],
                    "error": "Сторінка занадто велика."
                }

            html = response.text

            soup = BeautifulSoup(html, "html.parser")

            title = (
                soup.title.get_text(" ", strip=True).lower()
                if soup.title else ""
            )

            if (
                "robot check" in title
                or "captcha" in title
                or "sorry! something went wrong" in title
                or soup.select_one(
                    "form[action*='validateCaptcha']"
                )
            ):
                return {
                    "html": None,
                    "subcategories": [],
                    "error": "Amazon заблокував запит або показав CAPTCHA."
                }

            get_cache_path(category_id).write_text(
                html,
                encoding="utf-8"
            )

        except httpx.HTTPError as error:
            return {
                "html": None,
                "subcategories": [],
                "error": str(error)
            }

    subcategories = parse_categories(
        html,
        current_id=category_id
    )

    root_ids = {
        item["id"]
        for item in get_root_categories()
    }

    if category_id:
        subcategories = [
            item for item in subcategories
            if item["id"] not in root_ids
        ]

    return {
        "html": html,
        "subcategories": subcategories,
        "error": None
    }
