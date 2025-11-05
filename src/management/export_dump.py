from argparse import Namespace
from logging import getLogger
from pathlib import Path

from management.db.dump_data import dump_data
from management.s3.upload import upload

logger = getLogger(__name__)


def export_dump(args: Namespace) -> None:
    output_dir = args.output_dir
    file_name = args.file_name
    output_file = Path(output_dir).joinpath(file_name)

    db_dump = dump_data(output_file)
    if not args.local:
        upload(db_dump, args.bucket_name, args.bucket_path, args.s3_alias)
