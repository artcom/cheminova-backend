import argparse

from management.constants import bucket_alias, bucket_name, db_dump_path
from management.export_dump import export_dump


def export_dump_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("export-dump", help="Export dump to S3.")
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
    parser.set_defaults(func=export_dump)
