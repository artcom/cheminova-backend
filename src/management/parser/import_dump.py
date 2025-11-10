import argparse

from management.import_dump import import_dump


def import_dump_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("import-dump", help="Import dump from S3.")
    parser.add_argument(
        "-f",
        "--file-name",
        type=str,
        required=True,
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
    parser.set_defaults(func=import_dump)
