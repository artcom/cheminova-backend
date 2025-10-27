from django.db import models  # noqa F401
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.images import get_image_model_string
from wagtail.models import Page, Orderable
from wagtail.search.index import SearchField
from wagtail.fields import RichTextField
from modelcluster.fields import ParentalKey

__all__ = [
    "Characters",
    "Welcome",
    "WelcomeCharacter",
    "ChooseCharacter",
    "Introduction",
    "Photo",
    "Insight",
    "ExperienceIntro",
    "ExperienceGallery",
    "ExperienceCreate",
    "Collage",
    "LogbookRecord",
    "Timeline",
    "Reflection",
]


class Characters(Page):
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        InlinePanel("characters", label="Characters", min_num=3, max_num=3),
    ]
    api_fields = ["characters"]
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []
    max_count = 1


class Character(Orderable):
    page = ParentalKey(
        Characters,
        on_delete=models.CASCADE,
        related_name="characters",
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    approved_collection = models.ForeignKey(
        "wagtailcore.Collection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    not_approved_collection = models.ForeignKey(
        "wagtailcore.Collection",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    slug = models.CharField(max_length=30, blank=True, null=True)
    api_fields = ["name", "approved_collection", "not_approved_collection", "slug"]
    panels = [
        FieldPanel("name"),
        FieldPanel("approved_collection"),
        FieldPanel("not_approved_collection"),
        FieldPanel("slug"),
    ]


class Welcome(Page):
    description = models.CharField(max_length=255, blank=True, null=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    intro_text = RichTextField(blank=True, null=True)
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
        FieldPanel("intro_text"),
        FieldPanel("background_image"),
    ]
    api_fields = [
        "title",
        "description",
        "site_name",
        "intro_text",
        "background_image",
    ]
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["WelcomeCharacter"]
    max_count = 1


class WelcomeCharacter(Page):
    site_name = models.CharField(max_length=255, blank=True, null=True)
    onboarding = RichTextField(blank=True, null=True)
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
        FieldPanel("background_image"),
    ]
    api_fields = [
        "title",
        "site_name",
        "onboarding",
        "background_image",
    ]
    parent_page_types = ["Welcome"]
    subpage_types = ["ChooseCharacter"]
    max_count = 1


class ChooseCharacter(Page):
    character_type = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(blank=True, null=True)
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
        FieldPanel(
            "character_type", permission="experience.welcome_character.edit_restricted"
        ),
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("select_button_text"),
        FieldPanel(
            "character_image", permission="experience.welcome_character.edit_restricted"
        ),
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
    parent_page_types = ["WelcomeCharacter"]
    subpage_types = ["Introduction"]
    max_count = 3

    class Meta:
        permissions = [
            (
                "welcome_character.edit_restricted",
                "Can edit restricted fields - Welcome Character page",
            )
        ]


class Introduction(Page):
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
    subpage_types = ["Photo"]
    max_count_per_parent = 1


class Photo(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        InlinePanel(
            "image_descriptions", label="Image Descriptions", min_num=3, max_num=3
        ),
    ]
    api_fields = [
        "title",
        "heading",
        "image_descriptions",
    ]
    parent_page_types = ["Introduction"]
    subpage_types = ["Insight"]
    max_count_per_parent = 1


class ImageDescription(Orderable):
    page = ParentalKey(
        Photo,
        on_delete=models.CASCADE,
        related_name="image_descriptions",
    )
    short_description = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
    api_fields = ["short_description", "description"]
    panels = [FieldPanel("short_description"), FieldPanel("description")]


class Insight(Page):
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
        FieldPanel("character_image", permission="experience.insight.edit_restricted"),
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
    parent_page_types = ["Photo"]
    subpage_types = ["ExperienceIntro"]
    max_count_per_parent = 1

    class Meta:
        permissions = [
            (
                "insight.edit_restricted",
                "Can edit restricted fields - Insight page",
            )
        ]


class ExperienceIntro(Page):
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
    parent_page_types = ["Insight"]
    subpage_types = ["ExperienceGallery"]
    max_count_per_parent = 1


class ExperienceGallery(Page):
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
    parent_page_types = ["ExperienceIntro"]
    subpage_types = ["ExperienceCreate", "Collage", "LogbookRecord"]
    max_count_per_parent = 1


class Collage(Page):
    search_fields = Page.search_fields
    content_panels = Page.content_panels
    api_fields = [
        "title",
    ]
    parent_page_types = ["ExperienceGallery"]
    subpage_types = ["Reflection"]
    max_count_per_parent = 1


class LogbookRecord(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    record_button_text = models.CharField(max_length=20, blank=True, null=True)
    stop_button_text = models.CharField(max_length=10, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("record_button_text"),
        FieldPanel("stop_button_text"),
    ]
    api_fields = [
        "title",
        "heading",
        "record_button_text",
        "stop_button_text",
    ]
    parent_page_types = ["ExperienceGallery"]
    subpage_types = ["ExperienceCreate"]
    max_count_per_parent = 1


class ExperienceCreate(Page):
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
    parent_page_types = ["ExperienceGallery", "LogbookRecord"]
    subpage_types = ["Reflection"]
    max_count_per_parent = 1


class Timeline(Page):
    search_fields = Page.search_fields
    content_panels = Page.content_panels
    api_fields = [
        "title",
    ]
    parent_page_types = ["ExperienceCreate"]
    subpage_types = ["Reflection"]
    max_count_per_parent = 1


class Reflection(Page):
    reflection_text = RichTextField(null=True, blank=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("reflection_text"),
    ]
    api_fields = [
        "title",
        "reflection_text",
    ]
    parent_page_types = ["LogbookRecord", "Collage", "Timeline"]
    subpage_types = []
    max_count_per_parent = 1
