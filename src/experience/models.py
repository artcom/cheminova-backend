from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page, TranslatableMixin
from wagtail.search.index import SearchField

__all__ = [
    "Characters",
    "WelcomeLanguage",
    "WelcomeIntro",
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


class WelcomeLanguage(Page):
    choose_language_text = models.CharField(max_length=255, blank=True, null=True)
    content_panels = Page.content_panels + [
        FieldPanel("choose_language_text"),
        InlinePanel("languages", label="Languages", min_num=2, max_num=2),
    ]
    api_fields = ["title", "choose_language_text", "languages"]
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["WelcomeIntro"]
    max_count = 1


class Language(TranslatableMixin, Orderable):
    page = ParentalKey(
        WelcomeLanguage,
        on_delete=models.CASCADE,
        related_name="languages",
    )
    language_id = models.CharField(max_length=2, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    api_fields = ["language_id", "language"]
    panels = [FieldPanel("language_id"), FieldPanel("language")]


class WelcomeIntro(Page):
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
    background_image_layer_1 = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    background_image_layer_2 = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    background_image_layer_3 = models.ForeignKey(
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
        FieldPanel("background_image_layer_1"),
        FieldPanel("background_image_layer_2"),
        FieldPanel("background_image_layer_3"),
    ]
    api_fields = [
        "title",
        "description",
        "site_name",
        "intro_text",
        "background_image",
        "background_image_layer_1",
        "background_image_layer_2",
        "background_image_layer_3",
    ]
    parent_page_types = ["WelcomeLanguage"]
    subpage_types = ["Welcome"]
    max_count = 1


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
    parent_page_types = ["WelcomeIntro"]
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
            "character_type", permission="experience.choose_character.edit_restricted"
        ),
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("select_button_text"),
        FieldPanel(
            "character_image", permission="experience.choose_character.edit_restricted"
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
                "choose_character.edit_restricted",
                "Can edit restricted fields - Choose Character page",
            )
        ]


class Introduction(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    description = RichTextField(null=True, blank=True)
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
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel(
            "character_image", permission="experience.introduction.edit_restricted"
        ),
        FieldPanel("background_image"),
        FieldPanel("heading"),
        FieldPanel("description"),
        FieldPanel("image"),
    ]
    api_fields = [
        "title",
        "character_image",
        "background_image",
        "heading",
        "description",
        "image",
    ]
    parent_page_types = ["ChooseCharacter"]
    subpage_types = ["Photo"]
    max_count_per_parent = 1

    class Meta:
        permissions = [
            (
                "introduction.edit_restricted",
                "Can edit restricted fields - Introduction page",
            )
        ]


class Photo(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    continue_button_text = models.CharField(max_length=10, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("continue_button_text"),
        InlinePanel(
            "image_descriptions", label="Image Descriptions", min_num=3, max_num=3
        ),
    ]
    api_fields = [
        "title",
        "heading",
        "continue_button_text",
        "image_descriptions",
    ]
    parent_page_types = ["Introduction"]
    subpage_types = ["Insight"]
    max_count_per_parent = 1


class ImageDescription(TranslatableMixin, Orderable):
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
    parent_page_types = ["Insight"]
    subpage_types = ["ExperienceGallery"]
    max_count_per_parent = 1


class ExperienceGallery(Page):
    description = RichTextField(null=True, blank=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]
    api_fields = [
        "title",
        "description",
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
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
    ]
    api_fields = [
        "title",
        "heading",
    ]
    parent_page_types = ["ExperienceGallery"]
    subpage_types = ["ExperienceCreate"]
    max_count_per_parent = 1


class ExperienceCreate(Page):
    heading = models.CharField(max_length=255, blank=True, null=True)
    add_text_prompt = models.CharField(max_length=255, blank=True, null=True)
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("add_text_prompt"),
    ]
    api_fields = [
        "title",
        "heading",
        "add_text_prompt",
    ]
    parent_page_types = ["ExperienceGallery", "LogbookRecord"]
    subpage_types = ["Timeline", "Reflection"]
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
    return_to_monument_button_text = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )
    search_fields = Page.search_fields
    content_panels = Page.content_panels + [
        FieldPanel("reflection_text"),
        FieldPanel("return_to_monument_button_text"),
    ]
    api_fields = [
        "title",
        "reflection_text",
        "return_to_monument_button_text",
    ]
    parent_page_types = ["ExperienceCreate", "Collage", "Timeline"]
    subpage_types = []
    max_count_per_parent = 1
