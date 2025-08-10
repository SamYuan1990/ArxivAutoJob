"""Arxiv search functionality using the arxiv package."""

import arxiv
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def search_papers(
    search_query: str,
    categories: List[str] = None,
    date_from: datetime = None,
    date_to: datetime = None,
    max_results: int = 100
) -> List[Dict[str, Any]]:
    """
    Search for papers on arXiv.
    
    Args:
        search_query: Search query string
        categories: List of arXiv categories to search in
        date_from: Start date for search
        date_to: End date for search
        max_results: Maximum number of results to return
        
    Returns:
        List of paper dictionaries with id, title, authors, abstract, published date
    """
    # Build search query
    search_parts = [search_query] if search_query else []
    
    if categories:
        category_query = " OR ".join([f"cat:{cat}" for cat in categories])
        search_parts.append(f"({category_query})")
    
    # Use the correct date format for arXiv API
    # Handle date range properly - if both dates are provided, create a single range
    if date_from and date_to:
        # Both dates provided - create a range
        search_parts.append(f"submittedDate:[{date_from.strftime('%Y%m%d')}000000 TO {date_to.strftime('%Y%m%d')}235959]")
    elif date_from:
        # Only start date - search from that date onwards
        search_parts.append(f"submittedDate:[{date_from.strftime('%Y%m%d')}000000 TO *]")
    elif date_to:
        # Only end date - search up to that date
        search_parts.append(f"submittedDate:[* TO {date_to.strftime('%Y%m%d')}235959]")
    
    full_query = " AND ".join(search_parts) if search_parts else search_query
    
    logger.info(f"Searching arXiv with query: {full_query}")
    
    # Create search client
    client = arxiv.Client(
        page_size=min(max_results, 100),
        delay_seconds=0.1,
        num_retries=3
    )
    
    # Execute search
    search = arxiv.Search(
        query=full_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    try:
        for result in client.results(search):
            paper = {
                "id": result.get_short_id(),
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary,
                "published": result.published.isoformat() if result.published else None,
                "updated": result.updated.isoformat() if result.updated else None,
                "categories": result.categories,
                "links": {
                    "pdf": result.pdf_url,
                    "abstract": result.entry_id
                }
            }
            papers.append(paper)
            
            if len(papers) >= max_results:
                break
                
    except Exception as e:
        logger.error(f"Error searching papers: {str(e)}")
        raise
    
    logger.info(f"Found {len(papers)} papers")
    return papers