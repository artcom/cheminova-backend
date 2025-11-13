import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from .users.dump import dump_users

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Dumps users to a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output-dir",
            type=str,
            default="/tmp/db-data",
            help="Output dir for the user export.",
        )
        parser.add_argument(
            "-f",
            "--file-name",
            type=str,
            default="users.json",
            help="Output file name for the user export.",
        )

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        file_name = options["file_name"]

        try:
            dump_users(output_dir / file_name)
        except Exception as e:
            raise CommandError(f"Error dumping users: {e}")
