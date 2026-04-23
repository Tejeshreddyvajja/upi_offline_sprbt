from __future__ import annotations

from typing import List
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text


class SqlWriter:
    def __init__(self, odbc_connection_string: str, table_name: str) -> None:
        self.table_name = table_name
        params = quote_plus(odbc_connection_string)
        self.engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    def ensure_table(self) -> None:
        schema_name, table_only = self._split_schema_table(self.table_name)
        create_sql = f"""
IF NOT EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = '{schema_name}' AND TABLE_NAME = '{table_only}'
)
BEGIN
    EXEC('CREATE TABLE {schema_name}.{table_only} (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        url_hash NVARCHAR(64) NOT NULL UNIQUE,
        title NVARCHAR(1000) NULL,
        source_name NVARCHAR(255) NULL,
        author NVARCHAR(255) NULL,
        published_at DATETIME2 NULL,
        url NVARCHAR(1500) NULL,
        description NVARCHAR(MAX) NULL,
        content NVARCHAR(MAX) NULL,
        keywords NVARCHAR(500) NULL,
        ingested_at DATETIME2 NOT NULL
    )')
END
"""
        with self.engine.begin() as conn:
            conn.execute(text(create_sql))

    def upsert_dataframe(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0

        insert_sql = f"""
INSERT INTO {self.table_name}
(url_hash, title, source_name, author, published_at, url, description, content, keywords, ingested_at)
SELECT
    :url_hash, :title, :source_name, :author, :published_at, :url, :description, :content, :keywords, :ingested_at
WHERE NOT EXISTS (
    SELECT 1 FROM {self.table_name} t WHERE t.url_hash = :url_hash
)
"""

        rows: List[dict] = df.to_dict(orient="records")
        inserted_count = 0

        with self.engine.begin() as conn:
            for row in rows:
                result = conn.execute(text(insert_sql), row)
                inserted_count += result.rowcount

        return inserted_count

    @staticmethod
    def _split_schema_table(table_name: str) -> tuple[str, str]:
        if "." in table_name:
            schema_name, table_only = table_name.split(".", 1)
            return schema_name, table_only
        return "dbo", table_name
