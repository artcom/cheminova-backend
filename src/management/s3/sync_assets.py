import logging
import os
import subprocess
from argparse import Namespace
from pathlib import Path

logger = logging.getLogger(__name__)


def sync(args: Namespace) -> None:
    remove = ("--remove",) if args.remove else ()
    overwrite = ("--overwrite",) if args.overwrite else ()
    logger.info(
        f"Syncing assets from s3://{args.bucket_name}/{args.bucket_path} to /media using alias {args.s3_alias} with remove flag {args.remove}."
    )
    subprocess.run(
        [
            "mc",
            "mirror",
            *remove,
            *overwrite,
            f"{args.s3_alias}/{args.bucket_name}/{args.bucket_path}",
            args.media_path,
        ],
        env={
            "PATH": os.getenv("PATH"),
            "MC_CONFIG_DIR": Path(os.getenv("MC_CONFIG_PATH")).parent,
        },
        check=True,
    )
