"""Export the Flask pages as static files for GitHub Pages."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from app import app


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "docs"
STATIC_DIR = BASE_DIR / "static"


PAGES = {
    "/": ("index.html", ""),
    "/home": ("home/index.html", "../"),
    "/why": ("why/index.html", "../"),
    "/activities": ("activities/index.html", "../"),
    "/profiles": ("profiles/index.html", "../"),
}


def rewrite_absolute_urls(html: str, prefix: str) -> str:
    """Convert Flask absolute URLs to GitHub Pages-friendly relative URLs."""

    def replace_url(match: re.Match[str]) -> str:
        attr = match.group(1)
        value = match.group(2)
        if value.startswith("/static/"):
            rewritten = f"{prefix}static/{value.removeprefix('/static/')}"
        else:
            rewritten = {
                "/home": f"{prefix}home/",
                "/why": f"{prefix}why/",
                "/activities": f"{prefix}activities/",
                "/profiles": f"{prefix}profiles/",
                "/": prefix or "./",
            }.get(value, value)
        return f'{attr}="{rewritten}"'

    return re.sub(r'(href|src)="(/static/[^"]+|/home|/why|/activities|/profiles|/)"', replace_url, html)


def export_pages() -> None:
    """Render Flask routes and copy static assets into docs/."""

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static")

    client = app.test_client()

    for route, (relative_path, prefix) in PAGES.items():
        response = client.get(route)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to export {route}: {response.status_code}")

        output_path = OUTPUT_DIR / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            rewrite_absolute_urls(response.data.decode("utf-8"), prefix),
            encoding="utf-8",
        )

    (OUTPUT_DIR / "404.html").write_text(
        (OUTPUT_DIR / "index.html").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (OUTPUT_DIR / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    export_pages()
    print(f"Static site exported to: {OUTPUT_DIR}")
