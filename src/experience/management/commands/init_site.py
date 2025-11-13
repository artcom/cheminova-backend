import logging
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from .site.init import init_site

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Initializes the default Wagtail site with the provided site URL."

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--site-url",
            type=str,
            default=settings.SITE_URL,
            help="URL of the site to initialize.",
        )

    def handle(self, *args, **options):
        try:
            init_site(urlparse(options["site_url"]))
        except Exception as e:
            raise CommandError(f"Error initializing site: {e}")
