from logging import getLogger
from pathlib import Path

from ._session import get_bucket

logger = getLogger(__name__)


def download(db_dump: Path, bucket_name: str, bucket_path: str, s3_alias: str) -> None:
    bucket = get_bucket(s3_alias, bucket_name)

    bucket.download_file(f"{bucket_path}/{db_dump.name}", db_dump)
    logger.info(
        f"Imported dump from {bucket_name}/{bucket_path}/{db_dump.name} to {db_dump}"
    )
