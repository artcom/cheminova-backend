import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from .site.restore import restore_site

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--site-file",
            type=str,
            default="/tmp/db-data/site.json",
            help="Path to the site JSON file.",
        )

    def handle(self, *args, **options):
        site_file = Path(options["site_file"])

        try:
            restore_site(site_file)
        except Exception as e:
            raise CommandError(f"Error restoring site: {e}")
