import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from .db.restore_from_dump import restore_from_dump
from .s3.download import download

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import dump from S3."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_name",
            type=str,
            help="Input file for the database import.",
        )
        parser.add_argument(
            "-d",
            "--download-dir",
            type=str,
            default="/tmp/db-data",
            help="Directory to download the database dump.",
        )
        parser.add_argument(
            "-n",
            "--bucket-name",
            type=str,
            default="dev-cheminova",
            help="S3 bucket name for the database import.",
        )
        parser.add_argument(
            "-b",
            "--bucket-path",
            type=str,
            default="db-dump",
            help="S3 bucket path for the database import.",
        )
        parser.add_argument(
            "-a",
            "--s3-alias",
            type=str,
            default="dev-cheminova",
            help="S3 alias to use for the database import.",
        )

    def handle(self, *args, **options):
        file_name = options["file_name"]
        download_dir = Path(options["download_dir"])
        download_dir.mkdir(parents=True, exist_ok=True)
        bucket_name = options["bucket_name"]
        bucket_path = options["bucket_path"]
        s3_alias = options["s3_alias"]
        db_dump = download_dir.joinpath(file_name)

        try:
            download(db_dump, bucket_name, bucket_path, s3_alias)
            restore_from_dump(db_dump)
        except Exception as e:
            raise CommandError(f"Error importing dump: {e}")
