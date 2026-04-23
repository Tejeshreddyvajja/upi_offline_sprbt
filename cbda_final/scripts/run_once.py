from news_pipeline.config import Settings
from news_pipeline.orchestration.pipeline import run_pipeline
from news_pipeline.utils.logging_config import configure_logging


if __name__ == "__main__":
    settings = Settings()
    configure_logging(settings.log_level)
    summary = run_pipeline(settings)
    print(summary)
