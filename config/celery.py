import os

from celery import Celery
from django.conf import settings
from django_celery_beat.apps import BeatConfig
from django_celery_results.apps import CeleryResultConfig

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('config', broker=settings.CELERY_BROKER_URL)
      
app.config_from_object(os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development'))
app.autodiscover_tasks()

app.conf.update(result_extended=True)
app.conf.timezone = 'Europe/Moscow'

CeleryResultConfig.verbose_name = "Результаты Celery"
BeatConfig.verbose_name = "Периодические задачи"