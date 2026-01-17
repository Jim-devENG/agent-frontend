"""
Content detection using heuristics for target categories
"""
from typing import Dict, List
from bs4 import BeautifulSoup


class ArtDetector:
    """Detect if a website is in target categories using keyword heuristics"""
    
    # 1. Home Decor sites
    HOME_DECOR_KEYWORDS = [
        "interior decor", "interior decorating", "home decor", "decorating",
        "home decoration", "room decor", "decor ideas", "interior decorator",
        "decorative", "home styling", "interior styling", "decor tips",
        "furniture", "home accessories", "decorative arts", "home furnishings"
    ]
    
    # 2. Holiday sites
    HOLIDAY_KEYWORDS = [
        "holiday", "holiday planning", "holiday ideas", "holiday activities",
        "holiday travel", "holiday celebration", "holiday traditions",
        "seasonal decor", "holiday lifestyle", "holiday events"
    ]
    
    # 3. Parenting sites
    PARENTING_KEYWORDS = [
        "parenting", "parenting blog", "parenting tips", "parenting advice",
        "mom blog", "mother blog", "mommy blog", "family blog",
        "parenting lifestyle", "family activities", "parenting community",
        "mom lifestyle", "motherhood", "mom tips", "mom advice",
        "parenting tips", "family blog", "mommy lifestyle", "mom stories"
    ]
    
    # 4. Audio Visuals sites
    AUDIO_VISUALS_KEYWORDS = [
        "audio visual", "AV technology", "home theater", "sound system",
        "audio equipment", "visual technology", "home entertainment",
        "smart audio", "wireless speakers", "home audio", "visual display",
        "surround sound", "home cinema", "audio visual equipment"
    ]
    
    # 5. Gift Guides sites
    GIFT_GUIDES_KEYWORDS = [
        "gift guide", "gift ideas", "gift recommendations", "gift blog",
        "holiday gifts", "gift suggestions", "best gifts", "gift ideas blog",
        "gift guide website", "gift recommendations blog", "gift buying guide"
    ]
    
    # 6. Tech Innovation sites
    TECH_INNOVATION_KEYWORDS = [
        "tech innovation", "technology blog", "tech review", "innovation blog",
        "tech news", "technology news", "tech trends", "innovation technology",
        "tech blog", "technology innovation", "tech startup", "tech products",
        "tech innovation", "emerging technology", "tech solutions"
    ]
    
    # All relevant keywords combined (removed art_gallery)
    ALL_RELEVANT_KEYWORDS = (
        HOME_DECOR_KEYWORDS +
        HOLIDAY_KEYWORDS +
        PARENTING_KEYWORDS +
        AUDIO_VISUALS_KEYWORDS +
        GIFT_GUIDES_KEYWORDS +
        TECH_INNOVATION_KEYWORDS
    )
    
    def is_art_related(self, soup: BeautifulSoup, url: str, text_content: str = None) -> bool:
        """
        Detect if website is in target categories
        
        Categories: home_decor, holiday, parenting, audio_visuals, 
                   gift_guides, tech_innovation
        
        Args:
            soup: BeautifulSoup object
            url: URL of the page
            text_content: Optional pre-extracted text content
            
        Returns:
            True if relevant, False otherwise
        """
        if not soup and not text_content:
            return False
        
        # Extract text content if not provided
        if not text_content:
            text_content = soup.get_text().lower() if soup else ""
        
        url_lower = url.lower()
        combined_text = f"{url_lower} {text_content}"
        
        # Check for all relevant keywords
        keyword_count = sum(
            1 for keyword in self.ALL_RELEVANT_KEYWORDS
            if keyword in combined_text
        )
        
        # Check meta tags
        meta_keywords = self._extract_meta_keywords(soup)
        meta_keyword_count = sum(
            1 for keyword in self.ALL_RELEVANT_KEYWORDS
            if any(kw in meta.lower() for meta in meta_keywords for kw in [keyword])
        )
        
        # Check title and description
        title = ""
        description = ""
        if soup:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().lower()
            
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                description = meta_desc.get("content", "").lower()
        
        title_desc_count = sum(
            1 for keyword in self.ALL_RELEVANT_KEYWORDS
            if keyword in title or keyword in description
        )
        
        # Heuristic: If 3+ keywords found, likely relevant
        total_score = keyword_count + meta_keyword_count + title_desc_count
        return total_score >= 3
    
    def get_category(self, soup: BeautifulSoup, url: str, text_content: str = None) -> str:
        """
        Determine the specific category of the website
        
        Returns:
            Category: home_decor, holiday, parenting, audio_visuals, 
                     gift_guides, tech_innovation, or unknown
        """
        if not soup and not text_content:
            return "unknown"
        
        if not text_content:
            text_content = soup.get_text().lower() if soup else ""
        
        url_lower = url.lower()
        combined_text = f"{url_lower} {text_content}"
        
        # Count matches for each category
        home_decor_score = sum(1 for kw in self.HOME_DECOR_KEYWORDS if kw in combined_text)
        holiday_score = sum(1 for kw in self.HOLIDAY_KEYWORDS if kw in combined_text)
        parenting_score = sum(1 for kw in self.PARENTING_KEYWORDS if kw in combined_text)
        audio_visuals_score = sum(1 for kw in self.AUDIO_VISUALS_KEYWORDS if kw in combined_text)
        gift_guides_score = sum(1 for kw in self.GIFT_GUIDES_KEYWORDS if kw in combined_text)
        tech_innovation_score = sum(1 for kw in self.TECH_INNOVATION_KEYWORDS if kw in combined_text)
        
        # Return category with highest score
        scores = {
            "home_decor": home_decor_score,
            "holiday": holiday_score,
            "parenting": parenting_score,
            "audio_visuals": audio_visuals_score,
            "gift_guides": gift_guides_score,
            "tech_innovation": tech_innovation_score
        }
        
        max_category = max(scores, key=scores.get)
        return max_category if scores[max_category] > 0 else "unknown"
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tags"""
        keywords = []
        
        if soup:
            # Meta keywords tag
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            if meta_keywords:
                keywords.extend(meta_keywords.get("content", "").split(","))
            
            # Open Graph tags
            og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
            for tag in og_tags:
                content = tag.get("content", "")
                if content:
                    keywords.append(content)
        
        return [k.strip().lower() for k in keywords if k.strip()]
