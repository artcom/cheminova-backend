from logging import getLogger
from urllib.parse import ParseResult

from wagtail.models import Site

logger = getLogger(__name__)


def init_site(site_url: ParseResult):
    Site.objects.filter(is_default_site=True).update(
        hostname=site_url.hostname,
        port=site_url.port or (443 if site_url.scheme == "https" else 80),
        site_name=site_url.hostname,
    )
    logger.info(f"Initialized default site {site_url.hostname}")
