import logging

from django.core.management.base import BaseCommand, CommandError, CommandParser

from .users.admin import create_or_update_admin

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Create or update an admin user."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            required=True,
            help="Password for the admin user.",
        )
        parser.add_argument(
            "-u",
            "--username",
            default="admin",
            type=str,
            help="Username of the admin user. (default: admin)",
        )
        parser.add_argument(
            "-e",
            "--email",
            default="",
            type=str,
            help="Email address of the admin user. (default: empty)",
        )
        parser.add_argument(
            "-f",
            "--first-name",
            default="",
            type=str,
            help="First name of the admin user. (default: empty)",
        )
        parser.add_argument(
            "-l",
            "--last-name",
            default="",
            type=str,
            help="Last name of the admin user. (default: empty)",
        )

    def handle(self, *args, **options) -> None:
        try:
            create_or_update_admin(
                username=options["username"],
                email=options.get("email"),
                first_name=options.get("first_name"),
                last_name=options.get("last_name"),
                password=options["password"],
            )
        except Exception as e:
            raise CommandError(f"Error initializing admin user: {e}")
