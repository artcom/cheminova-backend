from argparse import Namespace
from pathlib import Path

from management.db.load_data import load_data
from management.s3.download import download


def import_dump(args: Namespace) -> None:
    file_name = args.file_name
    download_dir = args.download_dir
    db_dump = Path(download_dir).joinpath(file_name)
    download(db_dump, args.bucket_path)
    load_data(db_dump)
