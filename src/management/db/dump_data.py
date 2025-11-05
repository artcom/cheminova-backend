import datetime
from logging import getLogger
from pathlib import Path

import django

logger = getLogger(__name__)


def dump_data(output_file: Path) -> Path:
    django.setup()
    from django.core import management
    from django.core.management.commands import dumpdata

    output_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_name = f"{output_file.stem}_{timestamp}{output_file.suffix}"
    output_file = Path(output_file.parent).joinpath(timestamped_name)

    management.call_command(
        dumpdata.Command(),
        exclude=[
            "auth.user",
            "contenttypes.contenttype",
            "wagtailcore.site",
            "wagtailusers.userprofile",
            "sessions.session",
        ],
        format="json",
        indent=2,
        output=output_file,
    )

    logger.info(f"Database dump saved to {output_file}")

    return output_file
