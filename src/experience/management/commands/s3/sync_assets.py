import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def sync(
    media_path: str,
    bucket_name: str,
    bucket_path: str,
    s3_alias: str,
    remove: bool,
    to_s3: bool = False,
) -> None:
    bucket_uri = f"s3://{bucket_name}/{bucket_path}"
    source = media_path if to_s3 else bucket_uri
    target = bucket_uri if to_s3 else media_path

    logger.info(f"Syncing assets from {source} to {target}.")
    remove_arg = ("--delete",) if remove else ()
    subprocess.run(
        [
            "aws",
            "s3",
            "sync",
            *remove_arg,
            source,
            target,
        ],
        env={
            "PATH": os.getenv("PATH"),
            "AWS_CONFIG_FILE": os.getenv("S3_CONFIG_PATH"),
            "AWS_PROFILE": s3_alias,
        },
        check=True,
    )
