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
    to_s3: bool = False,
) -> None:
    source = media_path if to_s3 else f"{s3_alias}/{bucket_name}/{bucket_path}"
    target = f"{s3_alias}/{bucket_name}/{bucket_path}" if to_s3 else media_path

    logger.info(f"Syncing assets from {source} to {target}.")
    remove_arg = ("--remove",) if remove else ()
    overwrite_arg = ("--overwrite",) if overwrite else ()
    subprocess.run(
        [
            "mc",
            "mirror",
            *remove_arg,
            *overwrite_arg,
            source,
            target,
        ],
        env={
            "PATH": os.getenv("PATH"),
            "MC_CONFIG_DIR": Path(os.getenv("MC_CONFIG_PATH")).parent,
        },
        check=True,
    )
