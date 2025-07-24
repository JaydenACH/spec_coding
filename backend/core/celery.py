"""
Celery configuration for Respond IO Alternate Interface.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('respond_io_alternate')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression='gzip',
    result_compression='gzip',
    task_routes={
        'apps.messaging.tasks.*': {'queue': 'messaging'},
        'apps.notifications.tasks.*': {'queue': 'notifications'},
        'apps.files.tasks.*': {'queue': 'files'},
    },
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 