import json
import os
from logging import getLogger
from pathlib import Path

from boto3.session import Session
from botocore.client import Config

logger = getLogger(__name__)


def upload(db_dump: Path, bucket_name: str, bucket_path: str, s3_alias: str) -> None:
    config = json.loads(Path(os.environ.get("MC_CONFIG_PATH")).read_text())
    access_key = config["aliases"][s3_alias]["accessKey"]
    secret_key = config["aliases"][s3_alias]["secretKey"]
    endpoint_url = config["aliases"][s3_alias]["url"]
    secure = config["aliases"][s3_alias].get("secure", True)

    session = Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="europe-west3",
    )

    s3 = session.resource(
        "s3",
        endpoint_url=endpoint_url,
        config=Config(signature_version="s3v4"),
        verify=secure,
    )

    bucket = s3.Bucket(bucket_name)

    bucket.upload_file(db_dump, f"{bucket_path}/{db_dump.name}")
    logger.info(f"Exported dump to {bucket_name}/{bucket_path}/{db_dump.name}")
