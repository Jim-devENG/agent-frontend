"""
Scoring service - calculates prospect scores based on multiple factors
"""
import logging
from typing import Dict, Any, Optional
from decimal import Decimal

logger = logging.getLogger(__name__)


class ProspectScorer:
    """Service for calculating prospect scores"""
    
    # Weight configuration
    WEIGHTS = {
        "domain_authority": 0.30,  # 30% weight
        "has_email": 0.25,          # 25% weight
        "email_confidence": 0.15,   # 15% weight
        "topical_relevance": 0.15,  # 15% weight
        "data_quality": 0.10,       # 10% weight
        "recency": 0.05             # 5% weight
    }
    
    # Category keywords for relevance scoring
    CATEGORY_KEYWORDS = {
        "home_decor": ["home", "decor", "interior", "design", "furniture", "styling", "decorating"],
        "holiday": ["holiday", "seasonal", "christmas", "gift", "celebration", "festive"],
        "parenting": ["parent", "family", "kids", "children", "mom", "dad", "parenting"],
        "audio_visuals": ["audio", "visual", "AV", "theater", "sound", "video", "entertainment"],
        "gift_guides": ["gift", "guide", "present", "shopping", "buy", "purchase"],
        "tech_innovation": ["tech", "technology", "innovation", "gadget", "digital", "smart"]
    }
    
    def calculate_score(
        self,
        domain_authority: Optional[float] = None,
        has_email: bool = False,
        email_confidence: Optional[int] = None,
        page_title: Optional[str] = None,
        page_url: Optional[str] = None,
        categories: Optional[list] = None,
        dataforseo_payload: Optional[Dict] = None,
        hunter_payload: Optional[Dict] = None
    ) -> Decimal:
        """
        Calculate overall prospect score (0-100)
        
        Args:
            domain_authority: Domain Authority estimate (0-100)
            has_email: Whether prospect has contact email
            email_confidence: Email confidence score from Hunter.io (0-100)
            page_title: Page title for relevance scoring
            page_url: Page URL for relevance scoring
            categories: List of categories for relevance
            dataforseo_payload: Raw DataForSEO response
            hunter_payload: Raw Hunter.io response
        
        Returns:
            Decimal score (0-100)
        """
        scores = {}
        
        # 1. Domain Authority Score (0-100)
        if domain_authority is not None:
            scores["domain_authority"] = float(domain_authority)
        else:
            # Estimate from DataForSEO metrics if available
            if dataforseo_payload:
                metrics = dataforseo_payload.get("metrics", {})
                # Use backlinks or domain rating as proxy
                backlinks = metrics.get("backlinks", 0)
                if backlinks > 0:
                    # Rough estimate: more backlinks = higher DA
                    scores["domain_authority"] = min(100, (backlinks / 1000) * 50)  # Rough scaling
                else:
                    scores["domain_authority"] = 20  # Default low score
            else:
                scores["domain_authority"] = 20  # Default if no data
        
        # 2. Email Presence Score (0 or 100)
        scores["has_email"] = 100.0 if has_email else 0.0
        
        # 3. Email Confidence Score (0-100)
        if email_confidence is not None:
            scores["email_confidence"] = float(email_confidence)
        elif has_email and hunter_payload:
            # Extract confidence from Hunter.io payload
            emails = hunter_payload.get("emails", [])
            if emails:
                scores["email_confidence"] = float(emails[0].get("confidence_score", 50))
            else:
                scores["email_confidence"] = 50  # Default medium confidence
        else:
            scores["email_confidence"] = 0.0
        
        # 4. Topical Relevance Score (0-100)
        scores["topical_relevance"] = self._calculate_relevance_score(
            page_title, page_url, categories
        )
        
        # 5. Data Quality Score (0-100)
        scores["data_quality"] = self._calculate_data_quality_score(
            page_title, page_url, dataforseo_payload, hunter_payload
        )
        
        # 6. Recency Score (0-100) - Newer prospects get slight boost
        # This is a simple implementation - can be enhanced
        scores["recency"] = 100.0  # All prospects are "recent" for now
        
        # Calculate weighted score
        total_score = 0.0
        for factor, weight in self.WEIGHTS.items():
            factor_score = scores.get(factor, 0.0)
            total_score += factor_score * weight
            logger.debug(f"  {factor}: {factor_score:.2f} × {weight} = {factor_score * weight:.2f}")
        
        # Round to 2 decimal places
        final_score = Decimal(str(round(total_score, 2)))
        
        logger.debug(f"Final score: {final_score}")
        return final_score
    
    def _calculate_relevance_score(
        self,
        page_title: Optional[str],
        page_url: Optional[str],
        categories: Optional[list]
    ) -> float:
        """
        Calculate topical relevance score based on keywords
        
        Returns:
            Score from 0-100
        """
        if not categories:
            return 50.0  # Neutral score if no categories
        
        text_to_check = ""
        if page_title:
            text_to_check += page_title.lower() + " "
        if page_url:
            text_to_check += page_url.lower() + " "
        
        if not text_to_check:
            return 50.0
        
        # Count keyword matches
        matches = 0
        total_keywords = 0
        
        for category in categories:
            if category in self.CATEGORY_KEYWORDS:
                keywords = self.CATEGORY_KEYWORDS[category]
                total_keywords += len(keywords)
                for keyword in keywords:
                    if keyword in text_to_check:
                        matches += 1
        
        if total_keywords == 0:
            return 50.0
        
        # Score based on match ratio
        match_ratio = matches / total_keywords
        score = 50.0 + (match_ratio * 50.0)  # 50-100 range
        
        return min(100.0, max(0.0, score))
    
    def _calculate_data_quality_score(
        self,
        page_title: Optional[str],
        page_url: Optional[str],
        dataforseo_payload: Optional[Dict],
        hunter_payload: Optional[Dict]
    ) -> float:
        """
        Calculate data quality score based on available data
        
        Returns:
            Score from 0-100
        """
        score = 0.0
        factors = 0
        
        # Has page title
        if page_title and len(page_title.strip()) > 0:
            score += 20.0
        factors += 1
        
        # Has page URL
        if page_url and len(page_url.strip()) > 0:
            score += 20.0
        factors += 1
        
        # Has DataForSEO data
        if dataforseo_payload:
            score += 30.0
        factors += 1
        
        # Has Hunter.io data
        if hunter_payload:
            score += 30.0
        factors += 1
        
        # Normalize to 0-100
        if factors > 0:
            score = (score / factors) * 2.5  # Scale to 100
        
        return min(100.0, max(0.0, score))


def calculate_prospect_score(prospect_data: Dict[str, Any]) -> Decimal:
    """
    Convenience function to calculate score for a prospect
    
    Args:
        prospect_data: Dictionary with prospect data
    
    Returns:
        Decimal score (0-100)
    """
    scorer = ProspectScorer()
    
    return scorer.calculate_score(
        domain_authority=prospect_data.get("da_est"),
        has_email=bool(prospect_data.get("contact_email")),
        email_confidence=prospect_data.get("email_confidence"),
        page_title=prospect_data.get("page_title"),
        page_url=prospect_data.get("page_url"),
        categories=prospect_data.get("categories"),
        dataforseo_payload=prospect_data.get("dataforseo_payload"),
        hunter_payload=prospect_data.get("hunter_payload")
    )

