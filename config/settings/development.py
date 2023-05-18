from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']

MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":  BASE_DIR / "db.sqlite3",
        "USER": "user",
        "PASSWORD": "SQL_PASSWORD",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] + ['rest_framework.renderers.BrowsableAPIRenderer']


# django-debug-toolbar settings

INTERNAL_IPS = ["127.0.0.1"]


# Django CORS headers setttings

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True


# Redis settings

REDIS_URL = 'redis://localhost:6379/0'


# Cache settings

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    },
    'cache_table': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
    }
}

CACHING_TIME = 1 # 60


# Payment settings

QIWI_PRIVATE_KEY = ""

QIWI_PAYMENTS_LIFETIME = 30

SUCCESS_PAYMENT_URL = "http://127.0.0.1:8000/"


# Celery settings

CELERY_APP = 'config'

CELERY_BROKER_URL = REDIS_URL

CELERY_TASK_TRACK_STARTED = True

CELERY_TASK_TIME_LIMIT = 30 * 60

RESULT_BACKEND = REDIS_URL

CACHE_BACKEND = 'django-cache'

CELERYBEAT_SCHEDULE = {
    'payment_check_every_2_min': {
        'task': 'events.tasks.payment_handler',
        'schedule': crontab(minute='*/2'), # every 2 minutes
    },
    'send_registration_reminder_every_day': {
        'task': 'events.tasks.send_registration_reminder',
        'schedule': crontab(minute='*/2'), #crontab(hour=9, minute=0), # every day at 9am
    },
}

BEAT_SCHEDULE = CELERYBEAT_SCHEDULE

NOTIFICATION_DAYS_BEFORE_EVENTS = (5, 3, 1)


# Email settings

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'localhost'

EMAIL_PORT = '8025'

EMAIL_HOST_USER = 'from@example.com'

EMAIL_HOST_PASSWORD = None