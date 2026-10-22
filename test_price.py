
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "amazon_product.html"
IMAGE_DIR = BASE_DIR / "amazon_product_files"

html = HTML_FILE.read_text(
    encoding="utf-8",
    errors="replace"
)

soup = BeautifulSoup(html, "html.parser")

cards = soup.select(".a-button-inner")

print("Перевірка фотографій кольорів\n")

for card in cards:
    image = card.select_one("img.swatch-image")
    price = card.select_one(
        ".twister_swatch_price .olpWrapper"
    )

    if not image or not price:
        continue

    color = image.get("alt", "Невідомий")
    image_src = image.get("src", "")

    parsed = urlparse(image_src)
    image_path = parsed.path.replace("\\", "/")

    if "amazon_product_files/" in image_path:
        filename = image_path.split(
            "amazon_product_files/"
        )[-1]

        local_file = IMAGE_DIR / filename

        print("Колір:", color)
        print("Шлях HTML:", image_src)
        print("Локальний файл існує:", local_file.exists())
        print("Адреса для сайту:", "/amazon_product_files/" + filename)

    else:
        print("Колір:", color)
        print("Шлях HTML:", image_src)
        print("Зовнішнє зображення або інший шлях")

    print("-" * 40)
