import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def sync(
    media_path: str,
    bucket_name: str,
    bucket_path: str,
    s3_alias: str,
    remove: bool,
    overwrite: bool,
) -> None:
    logger.info(
        f"Syncing assets from s3://{bucket_name}/{bucket_path} to {media_path} using alias {s3_alias}."
    )
    remove = ("--remove",) if remove else ()
    overwrite = ("--overwrite",) if overwrite else ()
    subprocess.run(
        [
            "mc",
            "mirror",
            *remove,
            *overwrite,
            f"{s3_alias}/{bucket_name}/{bucket_path}",
            media_path,
        ],
        env={
            "PATH": os.getenv("PATH"),
            "MC_CONFIG_DIR": Path(os.getenv("MC_CONFIG_PATH")).parent,
        },
        check=True,
    )
