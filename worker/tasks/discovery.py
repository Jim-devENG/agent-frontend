"""
Discovery task - processes website discovery jobs using DataForSEO
"""
import asyncio
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

import sys
from pathlib import Path

# Add backend directory to path so we can import models
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))

from worker.clients.dataforseo import DataForSEOClient
from app.models.job import Job
from app.models.prospect import Prospect

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection (shared with backend)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def discover_websites_async(job_id: str) -> Dict[str, Any]:
    """
    Async function to discover websites for a job
    
    Args:
        job_id: UUID of the job to process
    
    Returns:
        Dictionary with results
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get job
            result = await db.execute(select(Job).where(Job.id == UUID(job_id)))
            job = result.scalar_one_or_none()
            
            if not job:
                logger.error(f"Job {job_id} not found")
                return {"success": False, "error": "Job not found"}
            
            # Update job status
            job.status = "running"
            await db.commit()
            
            params = job.params or {}
            keywords = params.get("keywords", "")
            raw_location = params.get("location", "usa") or "usa"
            max_results = params.get("max_results", 100)
            categories = params.get("categories", [])
            
            # Support multiple locations as comma-separated list, e.g. "usa,canada,germany"
            location_values = [
                loc.strip() for loc in str(raw_location).split(",") if loc and str(loc).strip()
            ]
            if not location_values:
                location_values = ["usa"]
            
            logger.info(
                f"Starting discovery job {job_id}: keywords='{keywords}', "
                f"locations={location_values}, categories={categories}"
            )
            
            # Initialize DataForSEO client
            try:
                client = DataForSEOClient()
            except ValueError as e:
                logger.error(f"DataForSEO client initialization failed: {e}")
                job.status = "failed"
                job.error_message = str(e)
                await db.commit()
                return {"success": False, "error": str(e)}
            
            # Generate search queries (shared across locations)
            search_queries = _generate_search_queries(keywords, categories)
            
            # Limit queries to avoid API rate limits
            search_queries = search_queries[:min(10, len(search_queries))]
            
            logger.info(f"Executing {len(search_queries)} search queries across {len(location_values)} locations")
            
            all_prospects = []
            discovered_domains = set()
            
            # For each selected location
            for loc in location_values:
                location_code = client.get_location_code(loc)
                logger.info(f"Using location '{loc}' with DataForSEO code {location_code}")
                
                # Search for each query in this location
                for query in search_queries:
                    try:
                        logger.info(f"Searching: '{query}' in location '{loc}'")
                        serp_result = await client.serp_google_organic(
                            keyword=query,
                            location_code=location_code,
                            depth=10
                        )
                        
                        if serp_result.get("success"):
                            results = serp_result.get("results", [])
                            logger.info(f"Found {len(results)} results for '{query}' in '{loc}'")
                            
                            for item in results:
                                url = item.get("url", "")
                                if not url or not url.startswith("http"):
                                    continue
                                
                                # Parse domain
                                parsed = urlparse(url)
                                domain = parsed.netloc.lower().replace("www.", "")
                                
                                # Skip if domain already discovered (across all locations)
                                if domain in discovered_domains:
                                    continue
                                
                                discovered_domains.add(domain)
                                
                                # Create prospect
                                prospect = Prospect(
                                    domain=domain,
                                    page_url=url,
                                    page_title=item.get("title", ""),
                                    da_est=None,  # Will be enriched later
                                    score=0,  # Will be calculated later
                                    outreach_status="pending",
                                    dataforseo_payload=item
                                )
                                
                                db.add(prospect)
                                all_prospects.append({
                                    "domain": domain,
                                    "url": url,
                                    "title": item.get("title", ""),
                                    "location": loc,
                                })
                                
                                # Limit total prospects
                                if len(all_prospects) >= max_results:
                                    break
                            
                            # Rate limiting between queries
                            await asyncio.sleep(2)
                        
                        else:
                            logger.warning(
                                f"Search failed for '{query}' in '{loc}': {serp_result.get('error')}"
                            )
                    
                    except Exception as e:
                        logger.error(f"Error processing query '{query}' in '{loc}': {str(e)}")
                        continue
                    
                    # Stop if we've reached max results
                    if len(all_prospects) >= max_results:
                        break
                
                # Stop across locations if we've reached max results
                if len(all_prospects) >= max_results:
                    break
            
            # Commit all prospects
            await db.commit()
            
            # Update job status
            job.status = "completed"
            job.result = {
                "prospects_found": len(all_prospects),
                "queries_executed": len(search_queries),
                "prospects": all_prospects[:10]  # Include first 10 for preview
            }
            await db.commit()
            
            logger.info(f"Discovery job {job_id} completed: {len(all_prospects)} prospects found")
            
            return {
                "success": True,
                "prospects_found": len(all_prospects),
                "job_id": job_id
            }
        
        except Exception as e:
            logger.error(f"Error in discovery job {job_id}: {str(e)}", exc_info=True)
            
            # Update job status to failed
            try:
                result = await db.execute(select(Job).where(Job.id == UUID(job_id)))
                job = result.scalar_one_or_none()
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    await db.commit()
            except:
                pass
            
            return {"success": False, "error": str(e)}


def discover_websites_task(job_id: str) -> Dict[str, Any]:
    """
    RQ task wrapper for website discovery
    
    This is the function that RQ will call
    
    Args:
        job_id: UUID string of the job to process
    
    Returns:
        Dictionary with results
    """
    return asyncio.run(discover_websites_async(job_id))


def _generate_search_queries(keywords: str, categories: List[str]) -> List[str]:
    """
    Generate search queries from keywords and categories
    
    Args:
        keywords: Base keywords
        categories: List of category filters
    
    Returns:
        List of search query strings
    """
    queries = []
    
    # Base query with keywords
    if keywords:
        queries.append(keywords)
    
    # Add category-specific queries
    category_keywords = {
        "home_decor": ["home decor", "interior design", "home styling"],
        "holiday": ["holiday decor", "seasonal", "holiday gifts"],
        "parenting": ["parenting blog", "family", "kids"],
        "audio_visuals": ["audio visual", "AV equipment", "home theater"],
        "gift_guides": ["gift guide", "gift ideas", "present guide"],
        "tech_innovation": ["tech innovation", "technology", "gadgets"]
    }
    
    for category in categories:
        if category in category_keywords:
            for kw in category_keywords[category]:
                if keywords:
                    queries.append(f"{keywords} {kw}")
                else:
                    queries.append(kw)
    
    # If no queries generated, use default
    if not queries:
        queries = ["art website", "creative blog", "design portfolio"]
    
    return queries[:20]  # Limit to 20 queries

