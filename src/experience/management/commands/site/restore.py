import json
from logging import getLogger
from pathlib import Path

from wagtail.models import Site

logger = getLogger(__name__)


def restore_site(input_file: Path) -> None:
    site_data = json.loads(input_file.read_text())
    Site.objects.filter(is_default_site=True).update(
        hostname=site_data["hostname"],
        port=site_data["port"],
        site_name=site_data["site_name"],
    )
    logger.info(f"Restored site {site_data['hostname']}")
