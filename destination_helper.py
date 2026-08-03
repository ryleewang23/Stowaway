"""
destination_helper.py

Fetches a representative destination photo from Wikipedia/Wikimedia.

No API key is required.
"""

from __future__ import annotations

import urllib.parse

import requests


WIKIPEDIA_SUMMARY_URL = (
    "https://en.wikipedia.org/api/rest_v1/page/summary/"
)

HEADERS = {
    "User-Agent": (
        "StowawayPackingApp/1.0 "
        "(educational travel packing project)"
    )
}

REQUEST_TIMEOUT = 15


def _candidate_titles(location):
    """Build likely Wikipedia page titles for a selected location."""
    name = str(location.get("name", "")).strip()
    admin1 = str(location.get("admin1", "")).strip()
    country = str(location.get("country", "")).strip()

    candidates = []

    if name and admin1:
        candidates.append(f"{name}, {admin1}")

    if name and country:
        candidates.append(f"{name}, {country}")

    if name:
        candidates.append(name)

    # Remove duplicates while preserving order.
    unique = []
    seen = set()

    for candidate in candidates:
        key = candidate.lower()

        if key not in seen:
            seen.add(key)
            unique.append(candidate)

    return unique


def get_destination_photo(location):
    """
    Returns destination-photo information.

    Result example:
    {
        "image_url": "...",
        "page_url": "...",
        "caption": "Tokyo, Japan",
        "source": "Wikipedia / Wikimedia Commons"
    }

    Returns None when no suitable image is available.
    """
    if not location:
        return None

    for title in _candidate_titles(location):
        encoded_title = urllib.parse.quote(
            title.replace(" ", "_"),
            safe=""
        )

        try:
            response = requests.get(
                WIKIPEDIA_SUMMARY_URL + encoded_title,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                continue

            data = response.json()

        except (
            requests.RequestException,
            ValueError
        ):
            continue

        # Disambiguation pages are not useful destination photos.
        if data.get("type") == "disambiguation":
            continue

        image = (
            data.get("originalimage")
            or data.get("thumbnail")
            or {}
        )

        image_url = image.get("source")

        if not image_url:
            continue

        page_url = (
            data.get("content_urls", {})
            .get("desktop", {})
            .get("page", "")
        )

        return {
            "image_url": image_url,
            "page_url": page_url,
            "caption": data.get(
                "title",
                location.get(
                    "display_name",
                    title
                )
            ),
            "source": (
                "Wikipedia / Wikimedia Commons"
            )
        }

    return None
