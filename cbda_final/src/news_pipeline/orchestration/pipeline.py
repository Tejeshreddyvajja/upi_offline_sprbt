from __future__ import annotations

import logging
from typing import Dict, Any

from news_pipeline.api.news_client import NewsClient
from news_pipeline.config import Settings
from news_pipeline.processing.transformer import normalize_articles
from news_pipeline.storage.blob_writer import BlobWriter
from news_pipeline.storage.sql_writer import SqlWriter


logger = logging.getLogger(__name__)


def run_pipeline(settings: Settings) -> Dict[str, Any]:
    settings.validate()

    client = NewsClient(
        base_url=settings.news_api_base_url,
        api_key=settings.news_api_key,
        query=settings.news_query,
        language=settings.news_language,
        sort_by=settings.news_sort_by,
        page_size=settings.news_page_size,
        max_pages=settings.news_max_pages,
        from_date=settings.news_from_date,
    )

    blob_writer = BlobWriter(
        connection_string=settings.azure_storage_connection_string,
        container_name=settings.azure_blob_container,
    )

    sql_writer = SqlWriter(
        odbc_connection_string=settings.azure_sql_odbc_connection_string,
        table_name=settings.azure_sql_table,
    )

    raw_payload = client.fetch_latest()
    blob_name = blob_writer.write_raw_payload(raw_payload)

    df = normalize_articles(raw_payload.get("articles", []), settings.keyword_filter)

    sql_writer.ensure_table()
    inserted_count = sql_writer.upsert_dataframe(df)

    summary = {
        "fetched_count": int(raw_payload.get("fetchedResults", 0)),
        "transformed_count": int(len(df.index)),
        "inserted_count": int(inserted_count),
        "raw_blob_path": blob_name,
        "target_table": settings.azure_sql_table,
    }

    logger.info("Pipeline summary: %s", summary)
    return summary
