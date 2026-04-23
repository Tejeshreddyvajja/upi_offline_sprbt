from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd


def _hash_url(url: str) -> str:
    return hashlib.sha256((url or "").encode("utf-8")).hexdigest()


def normalize_articles(raw_articles: List[Dict[str, Any]], keywords: List[str]) -> pd.DataFrame:
    if not raw_articles:
        return pd.DataFrame(
            columns=[
                "url_hash",
                "title",
                "source_name",
                "author",
                "published_at",
                "url",
                "description",
                "content",
                "keywords",
                "ingested_at",
            ]
        )

    records = []
    ingested_at = datetime.now(timezone.utc).isoformat()

    for article in raw_articles:
        source = article.get("source") or {}
        title = (article.get("title") or "").strip()
        description = (article.get("description") or "").strip()
        content = (article.get("content") or "").strip()
        url = (article.get("url") or "").strip()
        searchable = " ".join([title, description, content]).lower()

        matched_keywords = [kw for kw in keywords if kw in searchable] if keywords else []
        if keywords and not matched_keywords:
            continue

        records.append(
            {
                "url_hash": _hash_url(url),
                "title": title,
                "source_name": (source.get("name") or "").strip(),
                "author": (article.get("author") or "").strip(),
                "published_at": article.get("publishedAt"),
                "url": url,
                "description": description,
                "content": content,
                "keywords": ",".join(matched_keywords),
                "ingested_at": ingested_at,
            }
        )

    df = pd.DataFrame.from_records(records)
    if df.empty:
        return df

    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)

    # Drop duplicate URLs and hashes to keep ingestion idempotent.
    df = df.drop_duplicates(subset=["url_hash", "url"], keep="first")

    df = df.fillna("")
    return df
