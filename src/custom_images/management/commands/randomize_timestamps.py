import logging

from django.core.management.base import BaseCommand, CommandError

from .timestamps.randomize import randomize_timestamps

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Randomize image timestamps."

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--character",
            type=str,
            default=None,
            help="Character for the image timestamps randomization. If not provided, all characters will be considered.",
        )
        parser.add_argument(
            "-n",
            "--n-days",
            type=int,
            default=30,
            help="Number of days in the past to randomize timestamps within. (default: 30)",
        )

    def handle(self, *args, **options):
        try:
            randomize_timestamps(
                character=options["character"],
                n_days=options["n_days"],
            )
        except Exception as e:
            raise CommandError(f"Error randomizing timestamps: {e}")
