
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

AMAZON_URL = "https://www.amazon.com"


def parse_categories(html, current_id="", root_ids=None):
    soup = BeautifulSoup(html, "html.parser")
    root_ids = set(root_ids or [])

    categories = []
    seen = set()

    for link in soup.select("a[href*='/zgbs/']"):
        url = urljoin(AMAZON_URL, link.get("href", ""))
        parsed = urlparse(url)

        if parsed.hostname not in ("amazon.com", "www.amazon.com"):
            continue

        path = parsed.path.split("/ref=")[0].rstrip("/")

        if "/zgbs/" not in path:
            continue

        category_id = path.split("/zgbs/", 1)[1]

        if not category_id or category_id in seen:
            continue

        name = link.get_text(" ", strip=True)

        if not name or name.lower() == "main content":
            continue

        if current_id and category_id == current_id:
            continue

        if current_id and category_id in root_ids:
            continue

        seen.add(category_id)

        categories.append({
            "name": name,
            "id": category_id,
            "url": f"{parsed.scheme}://{parsed.netloc}{path}"
        })

    return categories
