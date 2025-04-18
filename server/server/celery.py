import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue, Exchange
import pendulum


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('air_tracker_celery')
app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.update(
    worker_name='gfs_stilt_worker',
    broker_url='redis://127.0.0.1:6379/0',
    result_expires=3600 * 24 * 30,
    worker_concurrency=1,
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',

    result_backend='django-db',
    result_extended=True,

    cache_backend='django-cache',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
    broker_connection_retry_on_startup=True,

    task_default_queue='default',
    task_default_routing_key='default',
    task_queues=(
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('gfs_stilt', Exchange('gfs_stilt'), routing_key='gfs_stilt'),
        Queue('wrf_stilt_aermod', Exchange('wrf_stilt_aermod'), routing_key='wrf_stilt_aermod'),
    ),

    task_routes={
        'gfs_stilt_task': {
            'queue': 'gfs_stilt',
            'routing_key': 'gfs_stilt',
        },
    },
    
)

# cron job
app.conf.beat_schedule = {
    'gfs_stilt_task': {
        'task': 'gfs_stilt_task',
        'schedule': crontab(minute=0, hour=3),
        'kwargs': {
            'run_date': pendulum.now().format("YYYY-MM-DD"),
            'receptor_ids': None
        },
    },
}

app.autodiscover_tasks(['apps.model_gfs_stilt.tasks'])