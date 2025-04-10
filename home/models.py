from django.db import models  # noqa F401
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail.search.index import SearchField


class Home(Page):
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    search_fields = Page.search_fields + [
        SearchField("title"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("image"),
    ]

    api_fields = [
        APIField("title"),
        APIField("image"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    max_count = 1
