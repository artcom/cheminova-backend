import os

from .base import *  # noqa F403
from .base import BASE_DIR

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SERVE_STATIC = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-rm=3^hc4v)26#@55+7gqkp6wc=3jo88t7sj$4u-)8c=5excl1r"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1", "http://127.0.0.1:8080", "http://localhost", "http://localhost:8080",
    "https://***REMOVED***"
]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WAGTAILADMIN_BASE_URL = "http://localhost:8080"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": "5432"
    }
}

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

BASE_PATH = os.environ.get("BASE_PATH", "/")
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
