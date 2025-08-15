from caseutil import to_camel, to_kebab, to_snake
from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers
from wagtail.images import get_image_model

from .models import (
    CharacterOverview,
    ChooseCharacter,
    IntroSearchAndCollect,
    PhotographyScreen,
    Welcome,
    YourCollection,
)


def absolute_url(relative_url: str) -> str:
    return settings.WAGTAILADMIN_BASE_URL + relative_url


def serialize(obj: models.Model) -> serializers.ModelSerializer:
    return globals()[f"{obj.__class__.__name__}ModelSerializer"](obj)


def get_serialized_data(child: models.Model, context: dict) -> dict:
    serializer = serialize(child)
    serializer.context.update(context)
    return serializer.data


def endpoint(obj: models.Model) -> str:
    return f"/{to_kebab(obj.__class__.__name__)}"


def to_camel_case_data(data: dict) -> dict:
    return {to_camel(key): value for key, value in data.items()}


def to_snake_case_data(data: dict) -> dict:
    return {to_snake(key): value for key, value in data.items()}


class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_image_model()
        fields = ["file"]


class CamelCaseMixin:
    def to_representation(self, *args, **kwargs):
        return to_camel_case_data(super().to_representation(*args, **kwargs))

    def to_internal_value(self, data):
        return super().to_internal_value(to_snake_case_data(data))


class PageModelSerializer(CamelCaseMixin, serializers.ModelSerializer):
    selfUrl = serializers.SerializerMethodField()
    # children_urls = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def get_selfUrl(self, obj: models.Model) -> str:
        return absolute_url(settings.API_BASE_URL + endpoint(obj) + f"/{obj.id}")

    def get_children_urls(self, obj: models.Model) -> list:
        children = obj.get_children().live().specific()
        children_urls = [
            data.get("selfUrl")
            for data in [serialize(child).data for child in children]
        ]
        return children_urls

    def get_children(self, obj: models.Model) -> list:
        query_params = self.context.get("query_params", {})
        if query_params.get("depth") is not None:
            if not self.context.get("iteration"):
                self.context.update(iteration=0)
            if self.context["iteration"] >= int(query_params.get("depth")):
                return self.get_children_urls(obj)
            else:
                children = obj.get_children().live().specific()
                self.context.update(iteration=self.context.get("iteration", 0) + 1)
                return [get_serialized_data(child, self.context) for child in children]
        else:
            children = obj.get_children().live().specific()
            return [get_serialized_data(child, self.context) for child in children]


def create_welcome_model_serializer():
    page_model_serializer_extra_fields = [
        "children",
        "selfUrl",
    ]
    image_field_names = [
        field.name
        for field in Welcome._meta.get_fields()
        if isinstance(field, models.fields.related.ForeignKey)
        and field.related_model == get_image_model()
    ]
    image_fields = {name: ImageModelSerializer() for name in image_field_names}

    class Meta:
        model = Welcome
        fields = Welcome.api_fields + page_model_serializer_extra_fields

    return type(
        "WelcomeModelSerializer",
        (PageModelSerializer,),
        {
            **image_fields,
            "Meta": Meta,
        },
    )


WelcomeModelSerializer = create_welcome_model_serializer()


class CharacterOverviewModelSerializer(PageModelSerializer):
    characters_image = ImageModelSerializer()
    background_image = ImageModelSerializer()

    class Meta:
        model = CharacterOverview
        fields = [
            "title",
            "heading",
            "site_name",
            "background_image",
            "characters_image",
            "onboarding",
            "children",
            "selfUrl",
        ]


class ChooseCharacterModelSerializer(PageModelSerializer):
    character_image = ImageModelSerializer()
    background_image = ImageModelSerializer()

    class Meta:
        model = ChooseCharacter
        fields = [
            "title",
            "character_type",
            "name",
            "character_image",
            "background_image",
            "children",
            "selfUrl",
        ]


class IntroSearchAndCollectModelSerializer(PageModelSerializer):
    image = ImageModelSerializer()

    class Meta:
        model = IntroSearchAndCollect
        fields = [
            "title",
            "heading",
            "description",
            "image",
            "children",
            "selfUrl",
        ]


class PhotographyScreenModelSerializer(PageModelSerializer):
    class Meta:
        model = PhotographyScreen
        fields = [
            "title",
            "heading",
            "description",
            "children",
            "selfUrl",
        ]


class YourCollectionModelSerializer(PageModelSerializer):
    imageDescriptions = serializers.SerializerMethodField()

    class Meta:
        model = YourCollection
        fields = [
            "title",
            "heading",
            "imageDescriptions",
            "selfUrl",
        ]

    def get_imageDescriptions(self, obj: YourCollection) -> list:
        return obj.image_descriptions.all().values_list("description", flat=True)


class QueryParamsSerializer(serializers.Serializer):
    depth = serializers.IntegerField(required=False)
