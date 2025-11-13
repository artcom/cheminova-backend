import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from .users.restore import restore_users

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Restores users from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--users-file",
            type=str,
            default="/tmp/db-data/users.json",
            help="Path to the users JSON file.",
        )

    def handle(self, *args, **options):
        users_file = Path(options["users_file"])

        try:
            restore_users(users_file)
        except Exception as e:
            raise CommandError(f"Error restoring users: {e}")
