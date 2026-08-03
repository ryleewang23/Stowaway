import urllib.parse


AMAZON_SEARCH_OVERRIDES = {
    "portable charger": "Anker portable charger",
    "sunscreen": "SPF 50 sunscreen",
    "extra sunscreen": "SPF 50 sunscreen",
    "water bottle": "insulated reusable water bottle",
    "hair brush": {
        "Women's essentials": "women's detangling hair brush",
        "Men's essentials": "men's hair brush",
        "General essentials": "hair brush"
    },
    "razor": {
        "Women's essentials": "women's razor",
        "Men's essentials": "men's razor",
        "General essentials": "razor"
    },
    "shaving cream": {
        "Women's essentials": "women's shaving cream",
        "Men's essentials": "men's shaving cream",
        "General essentials": "shaving cream"
    },
    "hiking boots": {
        "Women's essentials": "women's hiking boots",
        "Men's essentials": "men's hiking boots",
        "General essentials": "hiking boots"
    },
    "comfortable shoes": {
        "Women's essentials": "women's comfortable walking shoes",
        "Men's essentials": "men's comfortable walking shoes",
        "General essentials": "comfortable walking shoes"
    },
    "flip flops": {
        "Women's essentials": "women's flip flops",
        "Men's essentials": "men's flip flops",
        "General essentials": "flip flops"
    },
    "winter coat": {
        "Women's essentials": "women's winter coat",
        "Men's essentials": "men's winter coat",
        "General essentials": "winter coat"
    },
    "light jacket": {
        "Women's essentials": "women's light jacket",
        "Men's essentials": "men's light jacket",
        "General essentials": "light jacket"
    },
    "sweater": {
        "Women's essentials": "women's sweater",
        "Men's essentials": "men's sweater",
        "General essentials": "sweater"
    },
    "swimsuit": {
        "Women's essentials": "women's swimsuit",
        "Men's essentials": "men's swim trunks",
        "General essentials": "swimwear"
    },
    "business outfit": {
        "Women's essentials": "women's business outfit",
        "Men's essentials": "men's business outfit",
        "General essentials": "business outfit"
    }
}


GENDERED_CATEGORIES = {
    "Clothing",
    "Shoes"
}


GENDERED_ITEM_KEYWORDS = [
    "shirt",
    "top",
    "pants",
    "shorts",
    "underwear",
    "pajamas",
    "jacket",
    "coat",
    "sweater",
    "hoodie",
    "dress",
    "outfit",
    "thermal",
    "swimsuit",
    "shoes",
    "boots",
    "sandals",
    "sneakers",
    "flip flops",
    "razor",
    "shaving cream"
]


def amazon_search_term(
        item_name,
        packing_preference,
        category=None):
    clean_name = str(item_name).strip()
    item_key = clean_name.lower()

    override = AMAZON_SEARCH_OVERRIDES.get(item_key)

    if isinstance(override, dict):
        return override.get(
            packing_preference,
            clean_name
        )

    if isinstance(override, str):
        return override

    if packing_preference == "General essentials":
        return clean_name

    should_gender_search = (
        category in GENDERED_CATEGORIES
        or any(
            keyword in item_key
            for keyword in GENDERED_ITEM_KEYWORDS
        )
    )

    if not should_gender_search:
        return clean_name

    prefix = (
        "women's"
        if packing_preference == "Women's essentials"
        else "men's"
    )

    return f"{prefix} {clean_name}"


def amazon_link(
        item_name,
        packing_preference,
        category=None):
    search_term = amazon_search_term(
        item_name=item_name,
        packing_preference=packing_preference,
        category=category
    )

    query = urllib.parse.quote_plus(search_term)

    return f"https://www.amazon.com/s?k={query}"
