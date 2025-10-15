from django.db import models  # noqa F401
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.images import get_image_model_string
from wagtail.models import Page, Orderable
from wagtail.search.index import SearchField
from wagtail.fields import RichTextField
from modelcluster.fields import ParentalKey

__all__ = [
    "Welcome",
    "CharacterOverview",
    "ChooseCharacter",
    "IntroSearchAndCollect",
    "PhotographyScreen",
    "Exploration",
    "Conclusion",
    "UploadPage",
    "Gallery",
    "Ending",
]


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
        "title",
        "description",
        "site_name",
        "background_image",
    ]
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["CharacterOverview"]
    max_count = 1


class CharacterOverview(Page):
    site_name = models.CharField(max_length=255, blank=True, null=True)
    onboarding = RichTextField(blank=True, null=True)
    characters_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    background_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("site_name"),
        FieldPanel("onboarding"),
        FieldPanel("characters_image"),
        FieldPanel("background_image"),
    ]
    api_fields = [
        "title",
        "site_name",
        "onboarding",
        "characters_image",
        "background_image",
    ]
    parent_page_types = ["Welcome"]
    subpage_types = ["ChooseCharacter"]
    max_count = 1


class ChooseCharacter(Page):
    character_type = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    select_button_text = models.CharField(max_length=10, blank=True, null=True)
    character_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    background_image = models.ForeignKey(
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
        FieldPanel("select_button_text"),
        FieldPanel("character_image"),
        FieldPanel("background_image"),
    ]
    api_fields = [
        "title",
        "character_type",
        "name",
        "description",
        "select_button_text",
        "character_image",
        "background_image",
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
    api_fields = [
        "title",
        "heading",
        "description",
        "image",
    ]
    parent_page_types = ["ChooseCharacter"]
    subpage_types = ["PhotographyScreen"]
    max_count_per_parent = 1


class PhotographyScreen(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    take_photo_button_text = models.CharField(max_length=20, blank=True, null=True)
    retake_photo_button_text = models.CharField(max_length=20, blank=True, null=True)
    gallery_button_text = models.CharField(max_length=20, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("take_photo_button_text"),
        FieldPanel("retake_photo_button_text"),
        FieldPanel("gallery_button_text"),
        InlinePanel(
            "image_descriptions", label="Image Descriptions", min_num=3, max_num=3
        ),
    ]
    api_fields = [
        "title",
        "heading",
        "take_photo_button_text",
        "retake_photo_button_text",
        "gallery_button_text",
        "image_descriptions",
    ]
    parent_page_types = ["IntroSearchAndCollect"]
    subpage_types = ["Exploration"]
    max_count_per_parent = 1


class ImageDescription(Orderable):
    page = ParentalKey(
        PhotographyScreen,
        on_delete=models.CASCADE,
        related_name="image_descriptions",
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    api_fields = ["description"]
    panels = [FieldPanel("description")]


class Exploration(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
    character_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    top_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    bottom_image = models.ForeignKey(
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
        FieldPanel("character_image"),
        FieldPanel("top_image"),
        FieldPanel("bottom_image"),
    ]
    api_fields = [
        "title",
        "heading",
        "description",
        "character_image",
        "top_image",
        "bottom_image",
    ]
    parent_page_types = ["PhotographyScreen"]
    subpage_types = ["Conclusion"]
    max_count_per_parent = 1


class Conclusion(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("description"),
    ]
    api_fields = [
        "title",
        "heading",
        "description",
    ]
    parent_page_types = ["Exploration"]
    subpage_types = ["UploadPage"]
    max_count_per_parent = 1


class UploadPage(Page):
    description = RichTextField(null=True, blank=True)
    yes_button_text = models.CharField(max_length=5, blank=True, null=True)
    no_button_text = models.CharField(max_length=5, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("yes_button_text"),
        FieldPanel("no_button_text"),
    ]
    api_fields = [
        "title",
        "description",
        "yes_button_text",
        "no_button_text",
    ]
    parent_page_types = ["Conclusion"]
    subpage_types = ["Gallery"]
    max_count_per_parent = 1


class Gallery(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    exit_button_text = models.CharField(max_length=20, blank=True, null=True)
    close_button_text = models.CharField(max_length=10, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("exit_button_text"),
        FieldPanel("close_button_text"),
    ]
    api_fields = [
        "title",
        "heading",
        "exit_button_text",
        "close_button_text",
    ]
    parent_page_types = ["UploadPage"]
    subpage_types = ["Ending"]
    max_count_per_parent = 1


class Ending(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("description"),
    ]
    api_fields = [
        "title",
        "heading",
        "description",
    ]
    parent_page_types = ["Gallery"]
    subpage_types = []
    max_count_per_parent = 1
