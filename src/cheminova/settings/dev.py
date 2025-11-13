import os

from .base import *  # noqa F403
from .base import BASE_DIR, INSTALLED_APPS, MIDDLEWARE

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SERVE_STATIC = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-rm=3^hc4v)26#@55+7gqkp6wc=3jo88t7sj$4u-)8c=5excl1r"

WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", "http://localhost:8080")
SITE_URL = os.getenv("SITE_URL", WAGTAILADMIN_BASE_URL)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# Add CORS headers app for development
INSTALLED_APPS = INSTALLED_APPS + [
    "corsheaders",
]

# Add CORS middleware at the top of the middleware stack
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
] + MIDDLEWARE

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Vite dev server default
    "http://localhost:5173",  # Vite dev server alternative
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://***REMOVED***",  # Production frontend
]

# Allow credentials to be included in CORS requests (needed for Django sessions/CSRF)
CORS_ALLOW_CREDENTIALS = True

# Allow common headers that Vite/frontend might send
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "cache-control",
    "if-modified-since",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",  # Vite default port
    "http://localhost:5173",  # Vite alternative port
    "https://***REMOVED***",
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
        "PORT": "5432",
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
