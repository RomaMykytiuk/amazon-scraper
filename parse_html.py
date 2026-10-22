
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent


def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")

    cards = soup.select('div[data-csa-c-type="item"]')
    products = []

    for card in cards:
        title_element = card.select_one("h2")
        link_element = card.select_one("a:has(h2)")
        image_element = card.select_one("img.s-image")
        price_element = card.select_one(".a-price .a-offscreen")

        if not title_element or not link_element:
            continue

        title = title_element.get_text(" ", strip=True)
        link = link_element.get("href")

        if not title or not link:
            continue

        image = None

        if image_element:
            image_src = (
                image_element.get("src")
                or image_element.get("data-src")
            )

            if image_src:
                parsed = urlparse(image_src)
                image_path = parsed.path.replace("\\", "/")

                if "amazon_search_files/" in image_path:
                    filename = image_path.split(
                        "amazon_search_files/"
                    )[-1]

                    image = "/amazon_search_files/" + filename
                else:
                    image = urljoin(
                        "https://www.amazon.com",
                        image_src
                    )

        price = (
            price_element.get_text(strip=True)
            if price_element else None
        )

        products.append({
            "title": title,
            "price": price,
            "url": urljoin("https://www.amazon.com", link),
            "image": image
        })

        if len(products) == 5:
            break

    return products


if __name__ == "__main__":
    file_path = BASE_DIR / "amazon_search.html"

    html = file_path.read_text(
        encoding="utf-8",
        errors="replace"
    )

    products = parse_products(html)

    print("Знайдено товарів:", len(products))

    for product in products:
        print(product["title"])
        print("Фото:", product["image"])
