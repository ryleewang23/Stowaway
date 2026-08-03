"""
ai_helper.py

Uses OpenAI to interpret free-text activities and create specific,
categorized packing suggestions with concise reasons.
"""

import json
import os
import re

from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


load_dotenv()

DEFAULT_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini"
)


ALLOWED_CATEGORIES = [
    "Documents",
    "Clothing",
    "Shoes",
    "Toiletries",
    "Accessories",
    "Electronics",
    "Health & Safety",
    "Activity Gear",
    "Miscellaneous"
]


def existing_item_names(existing_items):
    names = []

    for item in existing_items or []:
        if isinstance(item, dict):
            name = (
                item.get("name")
                or item.get("item")
                or ""
            )
        else:
            name = str(item)

        name = str(name).strip()

        if name:
            names.append(name)

    return names


def extract_json_object(text):
    if not text:
        return None

    cleaned = str(text).strip()
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned
    )
    cleaned = re.sub(
        r"\s*```$",
        "",
        cleaned
    )

    try:
        value = json.loads(cleaned)

        if isinstance(value, dict):
            return value

    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        value = json.loads(
            cleaned[start:end + 1]
        )

        if isinstance(value, dict):
            return value

    except json.JSONDecodeError:
        return None

    return None


def normalize_items(
        raw_items,
        existing_items,
        number):
    if not isinstance(raw_items, list):
        return []

    existing_lower = {
        name.lower()
        for name in existing_item_names(
            existing_items
        )
    }

    results = []
    seen = set()

    for raw in raw_items:
        if not isinstance(raw, dict):
            continue

        name = str(
            raw.get("item")
            or raw.get("name")
            or ""
        ).strip()

        category = str(
            raw.get(
                "category",
                "Miscellaneous"
            )
        ).strip()

        reason = str(
            raw.get(
                "reason",
                ""
            )
        ).strip()

        key = name.lower()

        if not name:
            continue

        if key in existing_lower:
            continue

        if key in seen:
            continue

        if category not in ALLOWED_CATEGORIES:
            category = "Miscellaneous"

        results.append(
            {
                "item": name,
                "category": category,
                "reason": (
                    reason
                    or "Recommended for your specific activities."
                )
            }
        )

        seen.add(key)

        if len(results) >= number:
            break

    return results


def fallback_items(
        activities,
        existing_items,
        number):
    text = " ".join(
        str(activity)
        for activity in activities
    ).lower()

    candidates = []

    if any(
        word in text
        for word in [
            "nice dinner",
            "restaurant",
            "broadway",
            "theater",
            "theatre",
            "nightlife"
        ]
    ):
        candidates.extend(
            [
                {
                    "item": "1 Nice Dress or Dressy Outfit",
                    "category": "Clothing",
                    "reason": "Useful for the nicer evening plans you entered."
                },
                {
                    "item": "Dressier Shoes",
                    "category": "Shoes",
                    "reason": "Pairs with a polished dinner or event outfit."
                }
            ]
        )

    if any(
        word in text
        for word in [
            "walking",
            "sightseeing",
            "theme park",
            "disney",
            "shopping"
        ]
    ):
        candidates.extend(
            [
                {
                    "item": "Portable Charger",
                    "category": "Electronics",
                    "reason": "Long days using maps and photos can drain your phone."
                },
                {
                    "item": "Blister Bandages",
                    "category": "Health & Safety",
                    "reason": "Helpful when your itinerary involves lots of walking."
                }
            ]
        )

    if any(
        word in text
        for word in [
            "hiking",
            "trail",
            "camping"
        ]
    ):
        candidates.extend(
            [
                {
                    "item": "Moisture-Wicking Hiking Top",
                    "category": "Clothing",
                    "reason": "More comfortable during active outdoor plans."
                },
                {
                    "item": "Day Hiking Backpack",
                    "category": "Activity Gear",
                    "reason": "Carries water and trail essentials."
                }
            ]
        )

    candidates.extend(
        [
            {
                "item": "Small Day Bag",
                "category": "Accessories",
                "reason": "Keeps daily essentials organized while exploring."
            },
            {
                "item": "Travel-Size First-Aid Kit",
                "category": "Health & Safety",
                "reason": "Useful for handling minor issues while away."
            }
        ]
    )

    return normalize_items(
        raw_items=candidates,
        existing_items=existing_items,
        number=number
    )


def create_prompt(
        destination,
        days,
        weather_summary,
        activities,
        sex,
        existing_items,
        number):
    activity_lines = (
        "\n".join(
            f"- {activity}"
            for activity in activities
        )
        if activities
        else "- No activities entered."
    )

    existing_text = ", ".join(
        existing_item_names(existing_items)
    )

    return f"""
You are an expert travel stylist and packing assistant.

Create highly specific additions to a packing list.

Trip details:
Destination: {destination}
Trip length: {days} days
Weather: {weather_summary}
Packing preference: {sex or "General essentials"}

Planned activities:
{activity_lines}

Already packed or already recommended:
{existing_text}

Return:
- one personalized introduction
- up to {number} additional items

The recommendations must be specific.

Good clothing examples:
- "2 casual sundresses"
- "1 pair of lightweight linen pants"
- "2 dressier dinner outfits"
- "1 moisture-wicking hiking top"
- "1 lightweight cardigan"
- "1 pair of comfortable walking sneakers"

Avoid vague items such as:
- "clothes"
- "nice outfit"
- "pants"
- "shoes"

Choose garments that make sense for:
- the user's packing preference
- temperature and rain
- trip length
- the exact activities entered
- walking versus formal plans
- realistic outfit rewearing

Do not repeat anything already listed.

Allowed categories:
{", ".join(ALLOWED_CATEGORIES)}

Return valid JSON only:

{{
    "trip_intro": "A concise 1–2 sentence overview.",
    "items": [
        {{
            "item": "Specific item with useful quantity",
            "category": "One allowed category",
            "reason": "One short reason connected to the trip"
        }}
    ]
}}
""".strip()


def ai_suggestions(
        destination,
        days,
        weather_summary,
        activities,
        sex=None,
        existing_items=None,
        number=5):
    """
    Activities entered in the app are passed directly into this function.
    OpenAI uses them to create specific packing suggestions.
    """
    existing_items = (
        existing_items
        if existing_items is not None
        else []
    )

    try:
        number = int(number)
    except (TypeError, ValueError):
        number = 5

    number = max(
        1,
        min(number, 10)
    )

    fallback = fallback_items(
        activities=activities,
        existing_items=existing_items,
        number=number
    )

    fallback_intro = (
        f"Your {days}-day trip to {destination} has been "
        "organized around the weather and plans you entered."
    )

    if OpenAI is None:
        return {
            "trip_intro": fallback_intro,
            "items": fallback,
            "used_ai": False,
            "message": (
                "OpenAI is unavailable, so built-in suggestions were used."
            )
        }

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        return {
            "trip_intro": fallback_intro,
            "items": fallback,
            "used_ai": False,
            "message": (
                "No OpenAI API key was found, so built-in suggestions were used."
            )
        }

    prompt = create_prompt(
        destination=destination,
        days=days,
        weather_summary=weather_summary,
        activities=activities,
        sex=sex,
        existing_items=existing_items,
        number=number
    )

    try:
        client = OpenAI(
            api_key=api_key
        )

        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions=(
                "Return valid JSON only. Follow the requested schema."
            ),
            input=prompt
        )

        parsed = extract_json_object(
            response.output_text
        )

        if not parsed:
            return {
                "trip_intro": fallback_intro,
                "items": fallback,
                "used_ai": False,
                "message": (
                    "The AI response could not be read, so fallback suggestions were used."
                )
            }

        items = normalize_items(
            raw_items=parsed.get(
                "items",
                []
            ),
            existing_items=existing_items,
            number=number
        )

        trip_intro = str(
            parsed.get(
                "trip_intro",
                ""
            )
        ).strip()

        return {
            "trip_intro": (
                trip_intro
                or fallback_intro
            ),
            "items": (
                items
                or fallback
            ),
            "used_ai": True,
            "message": (
                "AI suggestions generated successfully."
            )
        }

    except Exception as error:
        return {
            "trip_intro": fallback_intro,
            "items": fallback,
            "used_ai": False,
            "message": (
                "The OpenAI request failed, so fallback suggestions were used. "
                f"Error: {error}"
            )
        }
