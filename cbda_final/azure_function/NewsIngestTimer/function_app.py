import azure.functions as func

from news_pipeline.config import Settings
from news_pipeline.orchestration.pipeline import run_pipeline
from news_pipeline.utils.logging_config import configure_logging


app = func.FunctionApp()


@app.timer_trigger(schedule="0 */15 * * * *", arg_name="mytimer", run_on_startup=False, use_monitor=True)
def ingest_news_timer(mytimer: func.TimerRequest) -> None:
    settings = Settings()
    configure_logging(settings.log_level)
    run_pipeline(settings)
