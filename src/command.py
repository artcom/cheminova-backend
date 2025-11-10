import argparse
import logging

from management.constants import bucket_alias
from management.parser.export_dump import export_dump_parser
from management.parser.import_dump import import_dump_parser
from management.parser.sync_assets import sync_assets_parser

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info(f"Using bucket alias: {bucket_alias}")
    parser = argparse.ArgumentParser(description="Django management script.")
    subparsers = parser.add_subparsers(help="subcommands")

    import_dump_parser(subparsers)
    export_dump_parser(subparsers)
    sync_assets_parser(subparsers)

    args = parser.parse_args()
    args.func(args)
