
from pathlib import Path
from urllib.parse import urljoin, urlparse
import re

from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
AMAZON_URL = "https://www.amazon.com"


def get_image_url(image, html_filename=None):
    if image is None:
        return None

    src = (
        image.get("data-src")
        or image.get("src")
        or ""
    )

    if src.startswith("data:") or not src:
        srcset = image.get("data-srcset") or image.get("srcset", "")

        if srcset:
            src = srcset.split(",")[0].strip().split(" ")[0]

    if not src or src.startswith("data:"):
        return None

    if src.startswith(("https://", "http://")):
        return src

    path = urlparse(src).path.replace("\\", "/")

    if "_files/" in path:
        folder, filename = path.rsplit("/", 1)
        folder = folder.split("/")[-1]

        if (BASE_DIR / folder / filename).is_file():
            return f"/{folder}/{filename}"

    return None


def parse_trending(html, limit=8, html_filename=None):
    soup = BeautifulSoup(html, "html.parser")

    products = []
    seen = set()

    links = soup.select("a[href*='/dp/']")

    for link in links:
        url = urljoin(
            AMAZON_URL,
            link.get("href", "")
        )

        match = re.search(
            r"/dp/([A-Za-z0-9]{10})",
            url
        )

        if not match:
            continue

        asin = match.group(1)

        if asin in seen:
            continue

        card = link.find_parent(
            "div",
            class_="p13n-sc-uncoverable-faceout"
        )

        if card is None:
            card = link.find_parent(
                attrs={"data-asin": asin}
            )

        if card is None:
            continue

        image = card.select_one("img")

        title = link.get_text(" ", strip=True)

        if not title:
            title_element = card.select_one(
                ".p13n-sc-truncate, ._cDEzb_p13n-sc-css-line-clamp-3_g3dy1"
            )

            if title_element:
                title = title_element.get_text(
                    " ", strip=True
                )

        if not title and image:
            title = image.get("alt", "").strip()

        if not title:
            continue

        price_element = card.select_one(
            ".a-price .a-offscreen"
        )

        price = (
            price_element.get_text(strip=True)
            if price_element else None
        )

        if not price:
            text = card.get_text(" ", strip=True)

            match_price = re.search(
                r"(?:offer|offers)\s+from\s+"
                r"(\$\s*\d+(?:\.\d{2})?)",
                text,
                re.IGNORECASE
            )

            if match_price:
                price = match_price.group(1).replace(" ", "")

        products.append({
            "title": title,
            "price": price,
            "image": get_image_url(
                image, html_filename
            ),
            "url": f"https://www.amazon.com/dp/{asin}"
        })

        seen.add(asin)

        if len(products) >= limit:
            break

    return products


if __name__ == "__main__":
    path = BASE_DIR / "amazon_trending.html"

    if path.is_file():
        html = path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        products = parse_trending(html)

        print("Знайдено товарів:", len(products))

        for product in products:
            print(product)
