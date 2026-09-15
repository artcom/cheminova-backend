from logging import getLogger
from pathlib import Path

from ._session import get_bucket

logger = getLogger(__name__)


def upload(db_dump: Path, bucket_name: str, bucket_path: str, s3_alias: str) -> None:
    bucket = get_bucket(s3_alias, bucket_name)

    bucket.upload_file(db_dump, f"{bucket_path}/{db_dump.name}")
    logger.info(f"Exported dump to {bucket_name}/{bucket_path}/{db_dump.name}")
