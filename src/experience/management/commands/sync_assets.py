import logging

from django.core.management.base import BaseCommand, CommandError

from .s3.sync_assets import sync

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    help = "Syncs media assets from S3."

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--s3-alias",
            type=str,
            default="dev-cheminova",
            help="S3 alias to use for syncing assets.",
        )
        parser.add_argument(
            "-n",
            "--bucket-name",
            type=str,
            default="dev-cheminova",
            help="S3 bucket name for syncing assets.",
        )
        parser.add_argument(
            "-b",
            "--bucket-path",
            type=str,
            default="media",
            help="S3 bucket path for syncing assets.",
        )
        parser.add_argument(
            "-m",
            "--media-path",
            type=str,
            default="/app/media",
            help="Local media path for syncing assets.",
        )
        parser.add_argument(
            "-r",
            "--remove",
            action="store_true",
            help="Remove local files not present in S3.",
        )
        parser.add_argument(
            "-o",
            "--overwrite",
            action="store_true",
            help="Overwrite local files with S3 files.",
        )

    def handle(self, *args, **options):
        media_path = options["media_path"]
        bucket_name = options["bucket_name"]
        bucket_path = options["bucket_path"]
        s3_alias = options["s3_alias"]
        remove = options["remove"]
        overwrite = options["overwrite"]
        try:
            sync(media_path, bucket_name, bucket_path, s3_alias, remove, overwrite)
        except Exception as e:
            raise CommandError(f"Error syncing assets: {e}")
