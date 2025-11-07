import argparse
import logging
import os

from management.export_dump import export_dump
from management.import_dump import import_dump

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bucket_alias = os.environ.get("BUCKET_ALIAS")
bucket_name = os.environ.get("BUCKET_NAME")
db_export_path = os.environ.get("DB_EXPORT_PATH")

if __name__ == "__main__":
    logger.info(f"Using bucket alias: {bucket_alias}")
    parser = argparse.ArgumentParser(description="Django management script.")
    subparsers = parser.add_subparsers(help="subcommands")

    parser_import_dump = subparsers.add_parser(
        "import-dump", help="Import dump from S3."
    )
    parser_import_dump.add_argument(
        "-f",
        "--file-name",
        type=str,
        required=True,
        help="Input file for the database import.",
    )
    parser_import_dump.add_argument(
        "-d",
        "--download-dir",
        type=str,
        default="/tmp/db-data",
        help="Directory to download the database dump.",
    )
    parser_import_dump.add_argument(
        "-n",
        "--bucket-name",
        type=str,
        default="dev-cheminova",
        help="S3 bucket name for the database import.",
    )
    parser_import_dump.add_argument(
        "-b",
        "--bucket-path",
        type=str,
        default="db-dump",
        help="S3 bucket path for the database import.",
    )
    parser_import_dump.add_argument(
        "-a",
        "--s3-alias",
        type=str,
        default="dev-cheminova",
        help="S3 alias to use for the database import.",
    )
    parser_import_dump.set_defaults(func=import_dump)

    parser_export_dump = subparsers.add_parser("export-dump", help="Export dump to S3.")
    parser_export_dump.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default="/tmp/db-data",
        help="Output directory for the database export.",
    )
    parser_export_dump.add_argument(
        "-f",
        "--file-name",
        type=str,
        default="data_dump.json",
        help="Output file for the database export.",
    )
    parser_export_dump.add_argument(
        "-a",
        "--s3-alias",
        type=str,
        default=bucket_alias,
        required=(bucket_alias is None),
        help="S3 alias to use for the database export.",
    )
    parser_export_dump.add_argument(
        "-n",
        "--bucket-name",
        type=str,
        default=bucket_name,
        required=(bucket_name is None),
        help="S3 bucket name for the database export.",
    )
    parser_export_dump.add_argument(
        "-b",
        "--bucket-path",
        type=str,
        default=db_export_path,
        required=(db_export_path is None),
        help="S3 bucket path for the database export.",
    )
    parser_export_dump.add_argument(
        "-l", "--local", action="store_true", help="Only store dump locally."
    )
    parser_export_dump.set_defaults(func=export_dump)

    args = parser.parse_args()
    args.func(args)
