import json
from logging import getLogger
from pathlib import Path

from wagtail.models import Site

logger = getLogger(__name__)


def dump_site(file: Path):
    site = (
        Site.objects.filter(is_default_site=True)
        .values("id", "hostname", "port", "site_name")
        .get()
    )
    file.write_text(json.dumps(site, indent=4))
    logger.info(f"Dumped site data to {file}")
