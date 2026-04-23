from news_pipeline.config import Settings
from news_pipeline.scheduler import start_scheduler
from news_pipeline.utils.logging_config import configure_logging


def main() -> None:
    settings = Settings()
    configure_logging(settings.log_level)
    start_scheduler(settings)


if __name__ == "__main__":
    main()
