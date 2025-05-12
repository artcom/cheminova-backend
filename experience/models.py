from django.db import models  # noqa F401
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.images import get_image_model_string
from wagtail.models import Page, Orderable
from wagtail.search.index import SearchField
from wagtail.fields import RichTextField
from modelcluster.fields import ParentalKey


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
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["CharacterOverview"]
    max_count = 1


class CharacterOverview(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
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
        FieldPanel("heading"),
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
    subpage_types = ["IntroSearchAndCollect"]
    max_count = 3


class IntroSearchAndCollect(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("description"),
        FieldPanel("image"),
    ]
    parent_page_types = ["ChooseCharacter"]
    subpage_types = ["PhotographyScreen"]
    max_count_per_parent = 1


class PhotographyScreen(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("description"),
    ]
    parent_page_types = ["IntroSearchAndCollect"]
    subpage_types = ["YourCollection"]
    max_count_per_parent = 1


class YourCollection(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        InlinePanel(
            "image_descriptions", label="Image Descriptions", min_num=3, max_num=3
        ),
    ]
    parent_page_types = ["PhotographyScreen"]
    max_count_per_parent = 1


class ImageDescription(Orderable):
    page = ParentalKey(
        YourCollection,
        on_delete=models.CASCADE,
        related_name="image_descriptions",
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    panels = [FieldPanel("description")]
