import logging

from django.core.management.base import BaseCommand, CommandError, CommandParser

from .s3.sync_assets import sync

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Syncs media assets between local storage and S3."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-3",
            "--s3-alias",
            type=str,
            default="dev-cheminova",
            help="S3 alias to use for syncing assets from. (default: dev-cheminova)",
        )
        parser.add_argument(
            "-n",
            "--bucket-name",
            type=str,
            default="dev-cheminova",
            help="S3 bucket name for syncing assets from. (default: dev-cheminova)",
        )
        parser.add_argument(
            "-u",
            "--bucket-path",
            type=str,
            default="media",
            help="S3 bucket path for syncing assets from. (default: media)",
        )
        parser.add_argument(
            "-m",
            "--media-path",
            type=str,
            default="/app/media",
            help="Local media path for syncing assets to. (default: /app/media)",
        )
        parser.add_argument(
            "-r",
            "--remove",
            action="store_true",
            help="Remove files not present in source.",
        )
        parser.add_argument(
            "-o",
            "--overwrite",
            action="store_true",
            help="Overwrite duplicate files.",
        )
        parser.add_argument(
            "-t",
            "--to-s3",
            action="store_true",
            help="Sync FROM local TO S3.",
        )

    def handle(self, *args, **options) -> None:
        media_path = options["media_path"]
        bucket_name = options["bucket_name"]
        bucket_path = options["bucket_path"]
        s3_alias = options["s3_alias"]
        remove = options["remove"]
        overwrite = options["overwrite"]
        to_s3 = options["to_s3"]
        try:
            sync(
                media_path,
                bucket_name,
                bucket_path,
                s3_alias,
                remove,
                overwrite,
                to_s3=to_s3,
            )
        except Exception as e:
            raise CommandError(f"Error syncing assets: {e}")
