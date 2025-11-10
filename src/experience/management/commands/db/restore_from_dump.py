import os
import subprocess
from logging import getLogger
from pathlib import Path

from django.conf import settings

logger = getLogger(__name__)


def restore_from_dump(dump_file: Path) -> None:
    logger.info(f"Restoring database from dump file: {dump_file}")
    subprocess.run(
        [
            "pg_restore",
            "--clean",
            "--dbname",
            settings.DATABASES["default"]["NAME"],
            "--host",
            settings.DATABASES["default"]["HOST"],
            "--port",
            str(settings.DATABASES["default"]["PORT"]),
            "--username",
            settings.DATABASES["default"]["USER"],
            str(dump_file),
        ],
        env={
            "PATH": os.getenv("PATH"),
            "PGPASSWORD": settings.DATABASES["default"]["PASSWORD"],
        },
        check=True,
    )
