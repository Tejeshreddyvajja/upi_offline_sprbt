from __future__ import annotations

import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from news_pipeline.config import Settings
from news_pipeline.orchestration.pipeline import run_pipeline


logger = logging.getLogger(__name__)


def start_scheduler(settings: Settings) -> None:
    scheduler = BackgroundScheduler()

    def _job_wrapper() -> None:
        try:
            run_pipeline(settings)
        except Exception:
            logger.exception("Scheduled pipeline run failed")

    scheduler.add_job(_job_wrapper, "interval", minutes=settings.schedule_interval_minutes)
    scheduler.start()
    logger.info("Scheduler started. Running every %s minutes", settings.schedule_interval_minutes)

    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
