from celery import Celery
import config

celery = Celery(__name__)
celery.config_from_object(config.CeleryConfig)
celery.conf.timezone = 'UTC'
celery.conf.beat_schedule = {
    "send-inference-results-back": {
        "task": "app.api.tasks.send_analysis_back_task",
        "schedule": 10.0
    }
}