"""APS Cyber Security Club homepage.

This Flask app intentionally keeps the attack surface small:
- no database
- no authentication
- no file upload
- no user-submitted content
- no outbound network calls

Only read-only JSON data is loaded from the local data directory.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template, url_for


# Resolve all project paths from this file so execution from another
# working directory cannot accidentally read a different data file.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_IMAGES_DIR = BASE_DIR / "static" / "images"
ACTIVITIES_PATH = DATA_DIR / "activities.json"


# Only plain filenames are accepted for JSON-provided images. This avoids
# remote URLs, absolute paths, ".." traversal, and nested path tricks.
SAFE_IMAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}\.(?:png|jpg|jpeg|webp|svg)$")


def create_app() -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Session cookies are not used by this app, but secure defaults are kept
    # in place in case Flask internals or future read-only features add one.
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", secrets.token_urlsafe(48)),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        MAX_CONTENT_LENGTH=1024 * 1024,
        JSON_AS_ASCII=False,
    )

    @app.after_request
    def set_security_headers(response):
        """Attach defensive HTTP headers to every response."""

        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self'; "
            "font-src 'self'; "
            "connect-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        return response

    @app.route("/")
    def intro():
        """Show the intro page first; no automatic redirect is used."""

        return render_template("intro.html", logo_available=logo_available())

    @app.route("/home")
    def home():
        """Render the main homepage."""

        recent_activities = load_activities()[:5]
        return render_template(
            "index.html",
            recent_activities=recent_activities,
            logo_available=logo_available(),
        )

    @app.route("/why")
    def why():
        """Render the APS promotion page."""

        return render_template("why.html", logo_available=logo_available())

    @app.route("/activities")
    def activities():
        """Render the read-only activity history page."""

        return render_template(
            "activities.html",
            activity_years=group_activities_by_year(load_activities()),
            logo_available=logo_available(),
        )

    @app.errorhandler(404)
    def not_found(_error):
        """Return a small static error page for unknown routes."""

        return render_template("base.html", error_message="페이지를 찾을 수 없습니다."), 404

    @app.errorhandler(500)
    def server_error(_error):
        """Avoid exposing stack traces or filesystem details to visitors."""

        return render_template("base.html", error_message="일시적인 오류가 발생했습니다."), 500

    return app


def logo_available() -> bool:
    """Return True only when the expected APS logo file exists locally."""

    return (STATIC_IMAGES_DIR / "aps_logo.png").is_file()


def load_activities() -> list[dict[str, Any]]:
    """Load and validate activities from the fixed JSON file.

    The path is constant and resolved under DATA_DIR to prevent path traversal.
    Invalid data is treated as a server-side configuration problem.
    """

    resolved_path = ACTIVITIES_PATH.resolve()
    if DATA_DIR.resolve() not in resolved_path.parents:
        abort(500)

    try:
        raw_data = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        abort(500)

    if not isinstance(raw_data, list):
        abort(500)

    activities = [validate_activity(item) for item in raw_data]
    return sorted(activities, key=lambda activity: activity["date"], reverse=True)


def group_activities_by_year(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group validated activities by year for timeline rendering."""

    grouped: dict[str, list[dict[str, Any]]] = {}
    for activity in activities:
        grouped.setdefault(activity["year"], []).append(activity)

    return [
        {"year": year, "items": grouped[year]}
        for year in sorted(grouped.keys(), reverse=True)
    ]


def validate_activity(item: Any) -> dict[str, Any]:
    """Validate one activity record before passing it to Jinja templates."""

    if not isinstance(item, dict):
        abort(500)

    required_text_fields = ("date", "title", "category")
    validated: dict[str, Any] = {}

    for field in required_text_fields:
        value = item.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > 180:
            abort(500)
        validated[field] = value.strip()

    date_value = validated["date"]
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", date_value):
        abort(500)

    validated["year"] = date_value[:4]
    validated["display_date"] = date_value[5:].replace("-", "/")

    organizer = item.get("organizer", "")
    if organizer:
        if not isinstance(organizer, str) or len(organizer.strip()) > 80:
            abort(500)
        validated["organizer"] = organizer.strip()
    else:
        validated["organizer"] = ""

    award = item.get("award", "")
    if award:
        if not isinstance(award, str) or len(award.strip()) > 40:
            abort(500)
        validated["award"] = award.strip()
    else:
        validated["award"] = ""

    if "participant" in item or "participants" in item:
        abort(500)

    return validated


app = create_app()


if __name__ == "__main__":
    # Debug is intentionally disabled by default to avoid exposing tracebacks.
    app.run(host="127.0.0.1", port=5000, debug=False)
