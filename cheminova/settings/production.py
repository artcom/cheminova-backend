import os

from .base import *  # noqa F403
from .base import BASE_DIR

DEBUG = False
SERVE_STATIC = False
WAGTAILADMIN_BASE_URL = "https://***REMOVED***/cms"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "***REMOVED***"]
SECRET_KEY = os.environ.get("SECRET_KEY")
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://localhost",
    "http://localhost:8080",
    "https://***REMOVED***",
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": "5432",
    }
}

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

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
