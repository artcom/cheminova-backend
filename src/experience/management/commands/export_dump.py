import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ._constants import bucket_alias, bucket_name, db_dump_path
from .db.dump_data import dump_data
from .s3.upload import upload

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output-dir",
            type=str,
            default="/tmp/db-data",
            help="Output directory for the database export.",
        )
        parser.add_argument(
            "-f",
            "--file-name",
            type=str,
            default="cheminova.dump",
            help="Output file for the database export.",
        )
        parser.add_argument(
            "-a",
            "--s3-alias",
            type=str,
            default=bucket_alias,
            required=(bucket_alias is None),
            help="S3 alias to use for the database export.",
        )
        parser.add_argument(
            "-n",
            "--bucket-name",
            type=str,
            default=bucket_name,
            required=(bucket_name is None),
            help="S3 bucket name for the database export.",
        )
        parser.add_argument(
            "-b",
            "--bucket-path",
            type=str,
            default=db_dump_path,
            required=(db_dump_path is None),
            help="S3 bucket path for the database export.",
        )
        parser.add_argument(
            "-l", "--local", action="store_true", help="Only store dump locally."
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]
        file_name = options["file_name"]
        output_file = Path(output_dir).joinpath(file_name)

        try:
            db_dump = dump_data(output_file)
            if not options["local"]:
                upload(
                    db_dump,
                    options["bucket_name"],
                    options["bucket_path"],
                    options["s3_alias"],
                )
        except Exception as e:
            raise CommandError(f"Error exporting dump: {e}")
