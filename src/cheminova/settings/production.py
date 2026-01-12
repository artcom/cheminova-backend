import os
from urllib.parse import urlparse

from .base import *  # noqa F403
from .base import BASE_DIR

DEBUG = False
SERVE_STATIC = False
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL")
SITE_URL = os.getenv("SITE_URL", WAGTAILADMIN_BASE_URL)

parsed_base_url = urlparse(WAGTAILADMIN_BASE_URL)
ALLOWED_HOSTS = ["localhost", "127.0.0.1", parsed_base_url.hostname]
SECRET_KEY = os.getenv("SECRET_KEY")
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://localhost",
    "http://localhost:8080",
    f"{parsed_base_url.scheme}://{parsed_base_url.netloc}",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": "5432",
    }
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

BASE_PATH = os.getenv("BASE_PATH", "/")
if BASE_PATH != "/":
    FORCE_SCRIPT_NAME = BASE_PATH
    SESSION_COOKIE_PATH = BASE_PATH

    LOGIN_URL = "login/"
    LOGIN_REDIRECT_URL = BASE_PATH
    LOGOUT_REDIRECT_URL = BASE_PATH

    STATIC_URL = f"{BASE_PATH}static/"

    STATIC_ROOT = os.path.join(BASE_DIR, "static/")

    # Media files
    MEDIA_URL = f"{BASE_PATH}media/"

    MEDIA_ROOT = os.path.join(BASE_DIR, "media/")
