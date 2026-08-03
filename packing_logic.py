"""
packing_logic.py

Builds the standard packing foundation using trip length,
Fahrenheit weather, packing preference, and free-text activities.

The function names remain compatible with the existing app.py.
"""

from datetime import date
import math


BASE_ITEMS = [
    "Passport / ID",
    "Phone",
    "Phone Charger",
    "Wallet",
    "Toothbrush",
    "Toothpaste",
    "Deodorant",
    "Hair Brush",
    "Shampoo",
    "Conditioner",
    "Pajamas"
]


def trip_length(start_date, end_date):
    """Returns the inclusive number of trip days."""
    if end_date < start_date:
        raise ValueError(
            "The end date must be on or after the start date."
        )

    return (end_date - start_date).days + 1


def activity_text(activities):
    """Combines free-text activities for simple rule matching."""
    return " ".join(
        str(activity)
        for activity in activities
    ).lower()


def clothing_amount(
        days,
        average_temperature,
        activities):
    """
    Creates more specific clothing quantities.

    AI will add nuanced activity items, while these rules provide
    a reliable clothing foundation.
    """
    text = activity_text(activities)

    tops = min(
        max(3, days),
        8
    )

    underwear = min(
        max(4, days + 1),
        10
    )

    socks = min(
        max(4, days + 1),
        10
    )

    casual_bottoms = min(
        max(2, math.ceil(days / 2)),
        5
    )

    items = [
        f"{tops} Casual Tops",
        f"{casual_bottoms} Casual Bottoms",
        f"{underwear} Pairs of Underwear",
        f"{socks} Pairs of Socks"
    ]

    dressy_keywords = [
        "nice dinner",
        "nice dinners",
        "restaurant",
        "nightlife",
        "broadway",
        "theater",
        "theatre",
        "wedding",
        "formal",
        "party",
        "club"
    ]

    business_keywords = [
        "business",
        "conference",
        "meeting",
        "interview",
        "work event"
    ]

    active_keywords = [
        "hiking",
        "workout",
        "gym",
        "running",
        "cycling",
        "sports"
    ]

    beach_keywords = [
        "beach",
        "swimming",
        "pool",
        "surfing",
        "snorkeling"
    ]

    if any(keyword in text for keyword in dressy_keywords):
        dressy_count = 2 if days >= 6 else 1
        items.append(
            f"{dressy_count} Dressier Outfits"
        )

    if any(keyword in text for keyword in business_keywords):
        business_count = min(
            max(1, math.ceil(days / 3)),
            3
        )
        items.append(
            f"{business_count} Business Outfits"
        )

    if any(keyword in text for keyword in active_keywords):
        workout_count = min(
            max(1, math.ceil(days / 3)),
            3
        )
        items.append(
            f"{workout_count} Activewear Outfits"
        )

    if any(keyword in text for keyword in beach_keywords):
        swimsuit_count = 2 if days >= 5 else 1
        items.append(
            f"{swimsuit_count} Swimsuits"
        )

    if average_temperature >= 85:
        items.extend(
            [
                "Lightweight Breathable Outfit",
                "Sun Hat"
            ]
        )

    elif average_temperature >= 70:
        items.append(
            "1 Light Layer"
        )

    elif average_temperature >= 50:
        items.extend(
            [
                "1 Sweater or Sweatshirt",
                "1 Light Jacket"
            ]
        )

    else:
        items.extend(
            [
                "1 Warm Coat",
                "2 Thermal Layers",
                "Scarf",
                "Beanie",
                "Gloves"
            ]
        )

    return items


def footwear_items(activities):
    """Adds more specific footwear based on entered activities."""
    text = activity_text(activities)

    items = [
        "Comfortable Walking Shoes"
    ]

    if any(
        keyword in text
        for keyword in [
            "hiking",
            "trail",
            "camping"
        ]
    ):
        items.append(
            "Hiking Boots"
        )

    if any(
        keyword in text
        for keyword in [
            "nice dinner",
            "restaurant",
            "nightlife",
            "formal",
            "wedding",
            "broadway",
            "theater",
            "theatre"
        ]
    ):
        items.append(
            "Dressier Shoes"
        )

    if any(
        keyword in text
        for keyword in [
            "beach",
            "pool",
            "swimming"
        ]
    ):
        items.append(
            "Sandals or Flip Flops"
        )

    return items


def personal_items(sex):
    """Adds preference-specific essentials."""
    preference = str(sex).lower()

    if preference == "female":
        return [
            "Makeup or Skincare Products",
            "Makeup Remover",
            "Hair Ties or Clips"
        ]

    if preference == "male":
        return [
            "Razor",
            "Shaving Products"
        ]

    return []


def weather_items(average_temperature):
    """Adds Fahrenheit-based weather essentials."""
    if average_temperature >= 85:
        return [
            "SPF 50 Sunscreen",
            "Cooling Towel"
        ]

    if average_temperature < 50:
        return [
            "Lip Balm",
            "Moisturizer"
        ]

    return []


def build_list(
        destination,
        start_date,
        end_date,
        sex,
        activities,
        average_temperature=72):
    """
    Returns the standard packing list expected by app.py.

    Specialized activity interpretation is also handled by AI,
    but this function supplies reliable quantities and basics.
    """
    days = trip_length(
        start_date,
        end_date
    )

    packing = []

    packing.extend(BASE_ITEMS)

    packing.extend(
        clothing_amount(
            days=days,
            average_temperature=average_temperature,
            activities=activities
        )
    )

    packing.extend(
        footwear_items(activities)
    )

    packing.extend(
        personal_items(sex)
    )

    packing.extend(
        weather_items(
            average_temperature
        )
    )

    # Preserve readable order while removing duplicates.
    final_items = []
    seen = set()

    for item in packing:
        key = item.strip().lower()

        if not key or key in seen:
            continue

        seen.add(key)
        final_items.append(item)

    return final_items


if __name__ == "__main__":
    start = date(2026, 8, 10)
    end = date(2026, 8, 16)

    result = build_list(
        destination="New York",
        start_date=start,
        end_date=end,
        sex="Female",
        activities=[
            "Walking around the city",
            "Two nice dinners",
            "Going to a Broadway show"
        ],
        average_temperature=82
    )

    for item in result:
        print("•", item)
