from logging import getLogger
from pathlib import Path

from boto3.session import Session
from botocore.client import Config

logger = getLogger(__name__)


def download(db_dump: Path, bucket_path: str) -> None:
    ACCESS_KEY = "minio"
    SECRET_KEY = "minio123"
    bucket_name = "db-dump"

    session = Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name="europe-west3",
    )

    s3 = session.resource(
        "s3",
        endpoint_url="http://s3:9000",
        config=Config(signature_version="s3v4"),
        region_name="europe-west3",
    )

    bucket = s3.Bucket(bucket_name)

    bucket.download_file(f"{bucket_path}/{db_dump.name}", db_dump)
    logger.info(
        f"Imported dump from {bucket_name}/{bucket_path}/{db_dump.name} to {db_dump}"
    )
