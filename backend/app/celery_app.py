from celery import Celery

from app.core.config import settings

celery = Celery(
    "meetmind",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.transcribe"],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
