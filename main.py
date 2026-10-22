
from pathlib import Path
import re

from fastapi import FastAPI, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path

from categories import (
    get_root_categories,
    get_category_name,
    get_category_info
)

BASE_DIR = Path(__file__).resolve().parent


from parse_trending import parse_trending

app = FastAPI()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

for folder in BASE_DIR.glob("*_files"):
    if folder.is_dir():
        app.mount(
            f"/{folder.name}",
            StaticFiles(directory=str(folder)),
            name=folder.name
        )


def category_data(category_id):
    if not re.fullmatch(r"[a-zA-Z0-9_/-]{0,120}", category_id):
        return {
            "products": [],
            "subcategories": [],
            "error": "Некоректний ID категорії."
        }

    info = get_category_info(category_id)

    if info["html"] is None:
        return {
            "products": [],
            "subcategories": [],
            "error": info["error"]
        }

    products = parse_trending(
        info["html"],
        limit=8
    )

    return {
        "products": products,
        "subcategories": info["subcategories"],
        "error": None
    }


@app.get("/")
def home():
    return RedirectResponse(url="/products")


@app.get("/products")
def products_page(
    request: Request,
    category: str = Query(default="")
):
    data = category_data(category)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "products": data["products"],
            "main_categories": get_root_categories(),
            "subcategories": data["subcategories"],
            "category_id": category,
            "category_name": get_category_name(category),
            "error": data["error"]
        }
    )


@app.get("/search")
def search(
    query: str = Query(default="trending"),
    category: str = Query(default="")
):
    data = category_data(category)

    return {
        "query": query,
        "category": category,
        "count": len(data["products"]),
        "products": data["products"],
        "error": data["error"]
    }
