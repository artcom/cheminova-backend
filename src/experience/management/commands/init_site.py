import logging
from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from .site.init import init_site

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Initializes the default Wagtail site with the provided site URL."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-i",
            "--site-url",
            type=str,
            default=settings.SITE_URL,
            help=f"URL of the site to initialize. (default: {settings.SITE_URL})",
        )

    def handle(self, *args, **options) -> None:
        try:
            init_site(urlparse(options["site_url"]))
        except Exception as e:
            raise CommandError(f"Error initializing site: {e}")
