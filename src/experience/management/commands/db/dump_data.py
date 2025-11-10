import datetime
import os
import subprocess
from logging import getLogger
from pathlib import Path

from django.conf import settings

logger = getLogger(__name__)


def dump_data(dump_file: Path) -> Path:
    dump_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_name = f"{dump_file.stem}_{timestamp}{dump_file.suffix}"
    dump_file = Path(dump_file.parent).joinpath(timestamped_name)

    logger.info(f"Dumping database to dump file: {dump_file}")

    subprocess.run(
        [
            "pg_dump",
            "--dbname",
            settings.DATABASES["default"]["NAME"],
            "--host",
            settings.DATABASES["default"]["HOST"],
            "--port",
            str(settings.DATABASES["default"]["PORT"]),
            "--username",
            settings.DATABASES["default"]["USER"],
            "--format",
            "custom",
            "--file",
            str(dump_file),
        ],
        env={
            "PATH": os.getenv("PATH"),
            "PGPASSWORD": settings.DATABASES["default"]["PASSWORD"],
        },
        check=True,
    )

    return dump_file
