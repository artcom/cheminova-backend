from argparse import Namespace
from pathlib import Path

from management.db.restore_from_dump import restore_from_dump
from management.s3.download import download


def import_dump(args: Namespace) -> None:
    file_name = args.file_name
    download_dir = Path(args.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    db_dump = download_dir.joinpath(file_name)
    download(db_dump, args.bucket_name, args.bucket_path, args.s3_alias)
    restore_from_dump(db_dump)
