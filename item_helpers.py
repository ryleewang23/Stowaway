import re
import uuid


CATEGORY_ORDER = [
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


CATEGORY_ICONS = {
    "Documents": "🪪",
    "Clothing": "👕",
    "Shoes": "👟",
    "Toiletries": "🪥",
    "Accessories": "🕶️",
    "Electronics": "🔌",
    "Health & Safety": "🩹",
    "Activity Gear": "🎒",
    "Miscellaneous": "📦"
}


def infer_category(item_name):
    name = str(item_name).strip().lower()

    keyword_groups = {
        "Documents": [
            "passport", "id", "wallet", "document",
            "confirmation", "ticket", "license", "visa"
        ],
        "Shoes": [
            "shoes", "boots", "flip flops",
            "sandals", "sneakers"
        ],
        "Clothing": [
            "shirt", "top", "pants", "bottom", "shorts",
            "underwear", "socks", "pajamas", "jacket",
            "coat", "sweater", "hoodie", "outfit",
            "dress", "thermal", "swimsuit", "activewear"
        ],
        "Toiletries": [
            "toothbrush", "toothpaste", "deodorant",
            "shampoo", "conditioner", "makeup", "razor",
            "shaving", "hair brush", "hair ties",
            "lotion", "skincare", "stain remover",
            "lip balm", "moisturizer"
        ],
        "Accessories": [
            "sunglasses", "hat", "scarf", "beanie",
            "gloves", "crossbody", "bag", "umbrella",
            "towel", "pouch"
        ],
        "Electronics": [
            "phone", "charger", "laptop", "camera",
            "adapter", "battery", "offline maps"
        ],
        "Health & Safety": [
            "sunscreen", "first-aid", "first aid",
            "bandage", "bug spray", "medicine",
            "medication", "aloe", "hand warmer",
            "emergency", "cooling towel", "ear protection"
        ],
        "Activity Gear": [
            "hiking", "ski", "snow", "goggles",
            "trail", "backpack", "snacks",
            "water bottle", "notebook",
            "presentation", "portfolio"
        ]
    }

    for category, keywords in keyword_groups.items():
        if any(
            keyword in name
            for keyword in keywords
        ):
            return category

    return "Miscellaneous"


def default_reason(
        item_name,
        category):
    """
    Gives standard items a useful reason so every checklist row
    can display supporting text, not only AI suggestions.
    """
    name = str(item_name).strip().lower()

    specific_reasons = {
        "passport / id": (
            "Needed for identification and travel check-in."
        ),
        "phone": (
            "Useful for maps, reservations, photos, and communication."
        ),
        "phone charger": (
            "Keeps your phone powered throughout the trip."
        ),
        "wallet": (
            "Keeps payment cards and identification together."
        ),
        "toothbrush": (
            "A daily personal-care essential."
        ),
        "toothpaste": (
            "A daily personal-care essential."
        ),
        "deodorant": (
            "Useful for staying comfortable during travel days."
        ),
        "pajamas": (
            "Provides comfortable sleepwear during the trip."
        ),
        "comfortable walking shoes": (
            "Supports long sightseeing and walking days."
        ),
        "dressier shoes": (
            "Pairs with nicer outfits for dinners or events."
        ),
        "hiking boots": (
            "Provides support and traction for trails."
        ),
        "spF 50 sunscreen".lower(): (
            "Helps protect exposed skin during sunny outdoor plans."
        )
    }

    if name in specific_reasons:
        return specific_reasons[name]

    if re.search(
        r"\bcasual tops?\b",
        name
    ):
        return (
            "Provides practical everyday outfit options."
        )

    if re.search(
        r"\bcasual bottoms?\b",
        name
    ):
        return (
            "Can be mixed and matched with multiple tops."
        )

    if "dressier outfit" in name:
        return (
            "Useful for nice dinners, shows, or evening plans."
        )

    if "business outfit" in name:
        return (
            "Appropriate for meetings or professional events."
        )

    if "activewear outfit" in name:
        return (
            "Useful for exercise, hiking, or active plans."
        )

    if "swimsuit" in name:
        return (
            "Needed for beach, pool, or water activities."
        )

    if "underwear" in name:
        return (
            "Includes an extra pair for convenience."
        )

    if "socks" in name:
        return (
            "Includes an extra pair for comfort and flexibility."
        )

    category_reasons = {
        "Documents": (
            "Important for identification, bookings, or travel access."
        ),
        "Clothing": (
            "Selected for the trip length, weather, and planned activities."
        ),
        "Shoes": (
            "Chosen to match the walking and activities in your plans."
        ),
        "Toiletries": (
            "Supports your normal personal-care routine while away."
        ),
        "Accessories": (
            "Adds convenience and comfort during daily outings."
        ),
        "Electronics": (
            "Supports communication, navigation, and entertainment."
        ),
        "Health & Safety": (
            "Helps you stay comfortable and prepared."
        ),
        "Activity Gear": (
            "Recommended for the activities in your itinerary."
        ),
        "Miscellaneous": (
            "A practical extra for keeping the trip organized."
        )
    }

    return category_reasons.get(
        category,
        "Recommended for this trip."
    )


def create_item(
        name,
        source="Standard",
        reason="",
        packed=False,
        category=None):
    chosen_category = (
        category
        or infer_category(name)
    )

    chosen_reason = (
        str(reason).strip()
        or default_reason(
            item_name=name,
            category=chosen_category
        )
    )

    return {
        "id": str(uuid.uuid4()),
        "name": str(name).strip(),
        "category": chosen_category,
        "source": source,
        "reason": chosen_reason,
        "packed": packed
    }


def remove_duplicate_names(items):
    result = []
    seen = set()

    for item in items:
        key = item["name"].strip().lower()

        if not key or key in seen:
            continue

        seen.add(key)
        result.append(item)

    return result


def normalize_ai_items(ai_items):
    """Keeps AI category and reason fields from ai_helper.py."""
    normalized = []

    for result in ai_items:
        if isinstance(result, dict):
            item_name = (
                result.get("item")
                or result.get("name")
                or ""
            )

            category = result.get(
                "category"
            )

            reason = result.get(
                "reason",
                ""
            )

        else:
            item_name = str(result)
            category = None
            reason = ""

        if item_name.strip():
            normalized.append(
                create_item(
                    name=item_name,
                    source="AI",
                    reason=reason,
                    category=category
                )
            )

    return normalized
