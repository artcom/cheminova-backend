import argparse
import logging

from management.export_dump import export_dump
from management.import_dump import import_dump

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Django management script.")
    subparsers = parser.add_subparsers(help="subcommands")

    parser_import_dump = subparsers.add_parser(
        "import-dump", help="Import dump from S3."
    )
    parser_import_dump.add_argument(
        "-f",
        "--file-name",
        type=str,
        default="data_dump.json",
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
        "-b",
        "--bucket-path",
        type=str,
        default="django-dump",
        help="S3 bucket path for the database import.",
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
        "-b",
        "--bucket-path",
        type=str,
        default="django-dump",
        help="S3 bucket path for the database export.",
    )
    parser_export_dump.add_argument(
        "-l", "--local", action="store_true", help="Only store dump locally."
    )
    parser_export_dump.add_argument(
        "-n",
        "--no-timestamp",
        action="store_true",
        help="Do not add timestamp to the dump file name.",
    )
    parser_export_dump.set_defaults(func=export_dump)

    args = parser.parse_args()
    args.func(args)
