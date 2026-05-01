"""Tavily integration."""

from __future__ import annotations

import logging

from tavily import TavilyClient

from src.config import Settings
from src.models import SearchResult

logger = logging.getLogger(__name__)


class TavilySearcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = TavilyClient(api_key=settings.tavily_api_key)
        logger.debug("TavilySearcher initialized")

    def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        logger.info("Tavily search: query='%s', max_results=%s", query[:60], max_results or self.settings.max_search_results)
        response = self.client.search(
            query=query,
            topic="general",
            search_depth="advanced",
            max_results=max_results or self.settings.max_search_results,
            include_answer=False,
            include_raw_content=True,
        )
        results: list[SearchResult] = []
        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", "Untitled"),
                    url=item.get("url", ""),
                    content=item.get("content", "") or "",
                    raw_content=item.get("raw_content", "") or "",
                )
            )
        logger.info("Tavily returned %d results", len(results))
        return results
