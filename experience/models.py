from django.db import models  # noqa F401
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail.search.index import SearchField
from wagtail.fields import RichTextField


class Welcome(Page):
    description = models.CharField(max_length=255, blank=True, null=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    background_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    search_fields = Page.search_fields + [
        SearchField("site_name"),
    ]
    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("site_name"),
        FieldPanel("background_image"),
    ]
    api_fields = [
        APIField("title"),
        APIField("site_name"),
        APIField("background_image"),
        APIField("description"),
    ]
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["CharacterOverview"]
    max_count = 1


class CharacterOverview(Page):
    onboarding = RichTextField()
    characters_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("onboarding"),
        FieldPanel("characters_image"),
    ]
    parent_page_types = ["Welcome"]
    subpage_types = ["ChooseCharacter"]
    max_count = 1


class ChooseCharacter(Page):
    character_type = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    character_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    search_fields = Page.search_fields + [
        SearchField("name"),
        SearchField("character_type"),
    ]
    content_panels = Page.content_panels + [
        FieldPanel("character_type"),
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("character_image"),
    ]
    parent_page_types = ["CharacterOverview"]
    max_count = 3
