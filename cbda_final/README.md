# News Data Pipeline to Azure (Production-Ready Template)

This project builds a modular Python data pipeline that:
1. Fetches latest news from a News API with pagination and retry handling.
2. Cleans/transforms data with pandas and removes duplicates.
3. Stores raw payload in Azure Blob Storage and structured records in Azure SQL Database.
4. Runs once or on a schedule.

## Architecture

- `src/news_pipeline/api/news_client.py`: News API integration, pagination, API-limit-safe requests.
- `src/news_pipeline/processing/transformer.py`: cleaning, keyword filtering, deduplication, schema normalization.
- `src/news_pipeline/storage/blob_writer.py`: uploads raw JSON to Azure Blob Storage.
- `src/news_pipeline/storage/sql_writer.py`: creates table if missing and inserts new records (idempotent by URL hash).
- `src/news_pipeline/orchestration/pipeline.py`: orchestrates end-to-end flow.
- `src/news_pipeline/scheduler.py`: periodic scheduled execution.
- `dashboard/streamlit_app.py`: optional dashboard for quick analytics.

## Why these Azure services

- **Azure Blob Storage**
  - Low-cost, highly durable storage for raw API responses.
  - Good for lineage and replay if transformation logic changes.
- **Azure SQL Database**
  - Great for relational querying, filtering by keyword/date/source.
  - Easy integration with BI tools and SQL analytics.

## Folder Structure

```text
.
|-- .github/workflows/ci.yml
|-- azure_function/
|   |-- host.json
|   |-- local.settings.example.json
|   `-- NewsIngestTimer/function_app.py
|-- dashboard/streamlit_app.py
|-- data/sample_output/
|   |-- cleaned_news_sample.csv
|   `-- raw_news_sample.json
|-- scripts/run_once.py
|-- src/news_pipeline/
|   |-- api/news_client.py
|   |-- orchestration/pipeline.py
|   |-- processing/transformer.py
|   |-- scheduler.py
|   |-- storage/blob_writer.py
|   |-- storage/sql_writer.py
|   |-- config.py
|   `-- main.py
|-- .env.example
|-- requirements.txt
`-- README.md
```

## Setup Instructions

1. Create virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy env file and add your credentials:

```powershell
copy .env.example .env
```

3. Update `.env` with:
- `NEWS_API_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_SQL_ODBC_CONNECTION_STRING`

4. Run pipeline once:

```powershell
$env:PYTHONPATH = "src"
python scripts/run_once.py
```

5. Run scheduled mode (every N minutes from env):

```powershell
$env:PYTHONPATH = "src"
python -m news_pipeline.main
```

6. Optional dashboard:

```powershell
$env:PYTHONPATH = "src"
streamlit run dashboard/streamlit_app.py
```

7. Optional Azure Functions timer setup:

```powershell
cd azure_function
copy local.settings.example.json local.settings.json
func start
```

If using Azure Functions, keep `PYTHONPATH=../src` or package `src/news_pipeline` as part of function deployment.

## Sample Output

- Raw JSON blob path pattern:
  - `raw/news_YYYYMMDD_HHMMSS.json`
- SQL table:
  - `dbo.news_articles`
- Example transformed columns:
  - `url_hash`, `title`, `source_name`, `author`, `published_at`, `url`, `description`, `content`, `keywords`, `ingested_at`

## Production Scaling Notes

1. Move schedule from local APScheduler to Azure Functions Timer Trigger or Azure Data Factory.
2. Use Azure Key Vault for secrets, not `.env` in production.
3. Add dead-letter/retry queue for failed writes.
4. Partition Blob paths by date: `raw/year=YYYY/month=MM/day=DD/...`.
5. For high throughput, switch SQL writes to batch/staging + `MERGE`.
6. Add observability (Application Insights + structured logs + alerting).
7. Add CI/CD and IaC (Bicep/Terraform).

## Resume-Worthy Bullet Points

- Designed and implemented a modular Python news ingestion pipeline using News API, pandas, and Azure SDKs.
- Built idempotent ETL flow with deduplication, schema normalization, and incremental SQL ingestion.
- Implemented dual-layer storage strategy: raw JSON in Azure Blob and query-optimized records in Azure SQL.
- Engineered scheduled data collection with robust retry, pagination, and API limit handling.
- Added production-grade logging, config-driven deployment, and CI automation with GitHub Actions.
