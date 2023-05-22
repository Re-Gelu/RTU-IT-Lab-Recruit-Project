from .base import *

DEBUG = False

SECRET_KEY = 'change_me'

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME":  "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "db",
        "PORT": "5432",
    }
}

# Django CORS headers setttings

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True


# Redis settings

REDIS_URL = 'redis://redis:6379/0'


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

CACHING_TIME = 60


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
        'schedule': crontab(hour=9, minute=0), # every day at 9am
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

EMAIL_USE_TLS = True