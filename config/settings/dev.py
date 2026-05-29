"""Ustawienia srodowiska deweloperskiego."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["*"]

# W dev pozwalamy na wszystkie originy frontendu
CORS_ALLOW_ALL_ORIGINS = True

# Email do konsoli zamiast realnego SMTP
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# W dev mozna uruchamiac zadania Celery synchronicznie do debugowania
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
