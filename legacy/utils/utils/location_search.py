"""
Location-based search configuration and query generation
"""
from typing import List, Dict, Tuple
from enum import Enum


class Location(Enum):
    """Available search locations"""
    USA = "usa"
    CANADA = "canada"
    UK_LONDON = "uk_london"
    GERMANY = "germany"
    FRANCE = "france"
    EUROPE = "europe"  # General Europe (excluding specific countries)


# Location-specific search modifiers
LOCATION_MODIFIERS = {
    Location.USA: ["USA", "United States", "US", "American"],
    Location.CANADA: ["Canada", "Canadian"],
    Location.UK_LONDON: ["London", "UK", "United Kingdom", "British"],
    Location.GERMANY: ["Germany", "German", "Deutschland"],
    Location.FRANCE: ["France", "French", "Français"],
    Location.EUROPE: ["Europe", "European"]
}

# New category keywords (removed art_gallery)
CATEGORIES = {
    "home_decor": {
        "keywords": [
            "home decor", "home decoration", "interior design", "interior decor",
            "home styling", "decorating", "home furnishings", "room decor",
            "decor ideas", "home accessories", "furniture", "home design"
        ],
        "queries": [
            "home decor blog",
            "interior design blog",
            "home decoration website",
            "interior decorator",
            "home styling blog",
            "decorating blog",
            "home design blog"
        ]
    },
    "holiday": {
        "keywords": [
            "holiday", "holiday planning", "holiday ideas", "holiday activities",
            "holiday travel", "holiday celebration", "holiday traditions",
            "seasonal decor", "holiday lifestyle", "holiday events"
        ],
        "queries": [
            "holiday blog",
            "holiday planning website",
            "holiday ideas blog",
            "holiday travel blog",
            "seasonal decor blog",
            "holiday lifestyle blog"
        ]
    },
    "parenting": {
        "keywords": [
            "parenting", "parenting blog", "parenting tips", "parenting advice",
            "mom blog", "mother blog", "mommy blog", "family blog",
            "parenting lifestyle", "family activities", "parenting community"
        ],
        "queries": [
            "parenting blog",
            "mom blog",
            "parenting tips website",
            "family lifestyle blog",
            "mommy blog",
            "parenting advice blog"
        ]
    },
    "audio_visuals": {
        "keywords": [
            "audio visual", "AV technology", "home theater", "sound system",
            "audio equipment", "visual technology", "home entertainment",
            "smart audio", "wireless speakers", "home audio", "visual display"
        ],
        "queries": [
            "audio visual blog",
            "home theater blog",
            "audio equipment review",
            "smart audio blog",
            "home entertainment blog",
            "wireless speakers blog"
        ]
    },
    "gift_guides": {
        "keywords": [
            "gift guide", "gift ideas", "gift recommendations", "gift blog",
            "holiday gifts", "gift suggestions", "best gifts", "gift ideas blog",
            "gift guide website", "gift recommendations blog"
        ],
        "queries": [
            "gift guide blog",
            "gift ideas blog",
            "gift recommendations website",
            "holiday gift guide",
            "best gifts blog",
            "gift suggestions blog"
        ]
    },
    "tech_innovation": {
        "keywords": [
            "tech innovation", "technology blog", "tech review", "innovation blog",
            "tech news", "technology news", "tech trends", "innovation technology",
            "tech blog", "technology innovation", "tech startup", "tech products"
        ],
        "queries": [
            "tech innovation blog",
            "technology blog",
            "tech review blog",
            "innovation blog",
            "tech news website",
            "tech trends blog"
        ]
    }
}

# Social media platforms to search
SOCIAL_PLATFORMS = {
    "instagram": {
        "queries": [
            "instagram influencer",
            "instagram account",
            "instagram profile"
        ]
    },
    "tiktok": {
        "queries": [
            "tiktok creator",
            "tiktok influencer",
            "tiktok account"
        ]
    }
}


def generate_location_queries(
    location: Location,
    categories: List[str] = None,
    include_social: bool = True
) -> List[Tuple[str, str]]:
    """
    Generate search queries for a specific location
    
    Args:
        location: Location to search in
        categories: List of category keys to include (None = all)
        include_social: Whether to include social media queries
        
    Returns:
        List of (query, category) tuples
    """
    queries = []
    location_mods = LOCATION_MODIFIERS.get(location, [])
    
    # Use all categories if none specified
    if categories is None:
        categories = list(CATEGORIES.keys())
    
    # Generate queries for each category
    for category_key in categories:
        if category_key not in CATEGORIES:
            continue
            
        category_info = CATEGORIES[category_key]
        base_queries = category_info["queries"]
        
        # Add location-specific queries
        for base_query in base_queries:
            # Add queries with location modifiers
            for mod in location_mods[:2]:  # Use first 2 modifiers to avoid too many queries
                query = f"{base_query} {mod}"
                queries.append((query, category_key))
            
            # Also add base query (location will be inferred from results)
            queries.append((base_query, category_key))
    
    # Add social media queries if requested
    if include_social:
        for platform, platform_info in SOCIAL_PLATFORMS.items():
            for base_query in platform_info["queries"]:
                for mod in location_mods[:1]:  # Use first modifier for social
                    query = f"{base_query} {mod}"
                    queries.append((query, f"{platform}_social"))
    
    return queries


def get_all_locations() -> List[Dict[str, str]]:
    """Get all available locations as list of dicts"""
    return [
        {"value": Location.USA.value, "label": "United States"},
        {"value": Location.CANADA.value, "label": "Canada"},
        {"value": Location.UK_LONDON.value, "label": "London, UK"},
        {"value": Location.GERMANY.value, "label": "Germany"},
        {"value": Location.FRANCE.value, "label": "France"},
        {"value": Location.EUROPE.value, "label": "Europe (General)"}
    ]


def get_all_categories() -> List[Dict[str, str]]:
    """Get all available categories as list of dicts"""
    category_labels = {
        "home_decor": "Home Decor",
        "holiday": "Holiday",
        "parenting": "Parenting",
        "audio_visuals": "Audio Visuals",
        "gift_guides": "Gift Guides",
        "tech_innovation": "Tech Innovation"
    }
    
    return [
        {"value": key, "label": category_labels.get(key, key)}
        for key in CATEGORIES.keys()
    ]

