import argparse

from management.s3.sync_assets import sync


def sync_assets_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("sync-assets", help="Sync assets from S3 to local.")
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
    parser.set_defaults(func=sync)
