from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from typing import Dict, List, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


@dataclass
class NewsClient:
    base_url: str
    api_key: str
    query: str
    language: str = "en"
    sort_by: str = "publishedAt"
    page_size: int = 100
    max_pages: int = 5
    from_date: str = ""

    def __post_init__(self) -> None:
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    def fetch_latest(self) -> Dict[str, Any]:
        all_articles: List[Dict[str, Any]] = []
        total_results_reported = 0

        for page in range(1, self.max_pages + 1):
            params = {
                "q": self.query,
                "language": self.language,
                "sortBy": self.sort_by,
                "pageSize": self.page_size,
                "page": page,
            }
            if self.from_date:
                params["from"] = self.from_date

            headers = {"X-Api-Key": self.api_key}
            response = self.session.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            payload = response.json()
            status = payload.get("status")
            if status != "ok":
                raise RuntimeError(f"News API returned non-ok status: {status}")

            page_articles = payload.get("articles", [])
            total_results_reported = int(payload.get("totalResults", 0))
            all_articles.extend(page_articles)

            logger.info("Fetched page %s with %s articles", page, len(page_articles))

            # Respect API limits by spacing paginated calls.
            time.sleep(0.35)

            if len(page_articles) < self.page_size:
                break

        return {
            "status": "ok",
            "totalResults": total_results_reported,
            "fetchedResults": len(all_articles),
            "articles": all_articles,
        }
