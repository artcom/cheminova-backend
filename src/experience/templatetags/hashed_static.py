from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(name="hashed_static")
def hashed_static(path):
    """A static URL that keeps its content hash even while DEBUG is on.

    Django serves unhashed static URLs under DEBUG, and nginx puts a two hour cache header on
    them, so an edited admin asset keeps its URL and browsers sit on the stale copy. Asking for
    the hashed name makes every rebuild a new URL. Falls back to the plain URL when the asset
    has not been collected yet, so a missing file 404s rather than breaking the page.
    """
    try:
        return staticfiles_storage.url(path, force=True)
    except ValueError:
        return static(path)
