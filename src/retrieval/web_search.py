"""Tavily integration."""

from __future__ import annotations

import logging
import time

from tavily import TavilyClient

from src.config import Settings
from src.models import SearchResult

logger = logging.getLogger(__name__)


class TavilySearcher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = TavilyClient(api_key=settings.tavily_api_key)
        logger.debug("TavilySearcher initialized")

    def search(
        self,
        query: str,
        max_results: int | None = None,
        search_depth: str | None = None,
    ) -> list[SearchResult]:
        depth = search_depth if search_depth in {"basic", "advanced"} else self.settings.tavily_default_search_depth
        logger.info(
            "Tavily search: query='%s', search_depth=%s, max_results=%s",
            query[:60],
            depth,
            max_results or self.settings.max_search_results,
        )
        response = None
        for attempt in range(1, 4):
            try:
                response = self.client.search(
                    query=query,
                    topic="general",
                    search_depth=depth,
                    max_results=max_results or self.settings.max_search_results,
                    include_answer=False,
                    include_raw_content=True,
                )
                break
            except Exception as exc:
                logger.warning("Tavily search failed on attempt %d/3: %s", attempt, exc)
                if attempt == 3:
                    return []
                time.sleep(0.5 * attempt)

        results: list[SearchResult] = []
        for item in (response or {}).get("results", []):
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
