from logging import getLogger
from pathlib import Path

import django

logger = getLogger(__name__)


def load_data(db_dump: Path) -> None:
    django.setup()
    from django.core import management
    from django.core.management.commands import loaddata

    management.call_command(
        loaddata.Command(),
        db_dump,
        format="json",
    )
    logger.info(f"Database loaded from {db_dump}")
