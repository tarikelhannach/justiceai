from celery import Celery
import os
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    'judicial_system',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

celery_app.conf.task_routes = {
    'app.tasks.ocr_tasks.process_document_ocr': {'queue': 'cpu_intensive'},
    'app.tasks.ocr_tasks.index_document_elasticsearch': {'queue': 'io_bound'},
}

logger.info("Celery app configured successfully")
