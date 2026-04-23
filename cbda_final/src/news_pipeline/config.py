from dataclasses import dataclass
import os
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _split_csv(value: str) -> List[str]:
    if not value:
        return []
    return [item.strip().lower() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    news_api_base_url: str = os.getenv("NEWS_API_BASE_URL", "https://newsapi.org/v2/everything")
    news_query: str = os.getenv("NEWS_QUERY", "technology")
    news_language: str = os.getenv("NEWS_LANGUAGE", "en")
    news_sort_by: str = os.getenv("NEWS_SORT_BY", "publishedAt")
    news_page_size: int = int(os.getenv("NEWS_PAGE_SIZE", "100"))
    news_max_pages: int = int(os.getenv("NEWS_MAX_PAGES", "5"))
    news_from_date: str = os.getenv("NEWS_FROM_DATE", "")

    schedule_interval_minutes: int = int(os.getenv("SCHEDULE_INTERVAL_MINUTES", "15"))

    azure_storage_connection_string: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    azure_blob_container: str = os.getenv("AZURE_BLOB_CONTAINER", "news-raw")

    azure_sql_odbc_connection_string: str = os.getenv("AZURE_SQL_ODBC_CONNECTION_STRING", "")
    azure_sql_table: str = os.getenv("AZURE_SQL_TABLE", "dbo.news_articles")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    keyword_filter_raw: str = os.getenv("KEYWORD_FILTER", "")

    @property
    def keyword_filter(self) -> List[str]:
        return _split_csv(self.keyword_filter_raw)

    def validate(self) -> None:
        required = {
            "NEWS_API_KEY": self.news_api_key,
            "AZURE_STORAGE_CONNECTION_STRING": self.azure_storage_connection_string,
            "AZURE_SQL_ODBC_CONNECTION_STRING": self.azure_sql_odbc_connection_string,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
