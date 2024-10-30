import os
from celery import Celery
from django.conf import settings

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_alchemy_be.settings')

# Create Celery instance
app = Celery('data_alchemy_be')

# Load config from Django settings, prefix Celery config with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://redis:6379/0'
app.conf.result_backend = 'redis://redis:6379/0'
app.conf.timezone = settings.TIME_ZONE
print(f"Broker URL: {app.conf.broker_url}")
print(f"Result Backend: {app.conf.result_backend}")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

