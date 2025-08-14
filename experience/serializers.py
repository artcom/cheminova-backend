from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import (
    CharacterOverview,
    ChooseCharacter,
    IntroSearchAndCollect,
    PhotographyScreen,
    Welcome,
    YourCollection,
    model_endpoints,
)


def absolute_url(relative_url: str) -> str:
    return settings.WAGTAILADMIN_BASE_URL + relative_url


def serialize(obj: models.Model) -> serializers.ModelSerializer:
    return globals()[f"{obj.__class__.__name__}ModelSerializer"](obj)


def get_serialized_data(child):
    serializer = serialize(child)
    serializer.context.update(with_children=True)
    return serializer.data


class PageModelSerializer(serializers.ModelSerializer):
    selfUrl = serializers.SerializerMethodField()
    children_urls = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def endpoint(self, obj: models.Model) -> str:
        return f"/{model_endpoints.get(obj.__class__.__name__)}"

    def welcome_page(self, obj: models.Model) -> Welcome:
        return next(
            (
                ancestor
                for ancestor in obj.get_ancestors(inclusive=True).live().specific()
                if ancestor.get_content_type().model == "welcome"
            ),
            None,
        )

    def get_selfUrl(self, obj: models.Model) -> str:
        return absolute_url(settings.API_BASE_URL + self.endpoint(obj) + f"/{obj.id}")

    def get_children_urls(self, obj: models.Model) -> list:
        children = obj.get_children().live().specific()
        children_urls = [
            data.get("selfUrl")
            for data in [serialize(child).data for child in children]
        ]
        return children_urls

    def get_children(self, obj: models.Model) -> list:
        if (
            self.context.get("request")
            and self.context["request"]
            .query_params.get("withChildren", "false")
            .lower()
            == "true"
        ):
            self.context.update(with_children=True)
        with_children = self.context.get("with_children", False)
        if not with_children:
            return self.get_children_urls(obj)
        else:
            children = obj.get_children().live().specific()
            return [get_serialized_data(child) for child in children]


class WelcomeModelSerializer(PageModelSerializer):
    backgroundImageUrl = serializers.SerializerMethodField()
    siteName = serializers.SerializerMethodField()

    class Meta:
        model = Welcome
        fields = [
            "id",
            "title",
            "description",
            "siteName",
            "backgroundImageUrl",
            "children",
            "selfUrl",
        ]
        depth = 1

    def get_backgroundImageUrl(self, obj: Welcome) -> str:
        return (
            absolute_url(obj.background_image.file.url) if obj.background_image else ""
        )

    def get_siteName(self, obj: Welcome) -> str:
        return obj.site_name if obj.site_name else ""


class CharacterOverviewModelSerializer(PageModelSerializer):
    charactersImageUrl = serializers.SerializerMethodField()
    backgroundImageUrl = serializers.SerializerMethodField()
    siteName = serializers.SerializerMethodField()

    class Meta:
        model = CharacterOverview
        fields = [
            "id",
            "title",
            "heading",
            "siteName",
            "backgroundImageUrl",
            "charactersImageUrl",
            "onboarding",
            "children",
            "selfUrl",
        ]
        depth = 1

    def get_charactersImageUrl(self, obj: CharacterOverview) -> str:
        return (
            absolute_url(obj.characters_image.file.url) if obj.characters_image else ""
        )

    def get_siteName(self, obj: CharacterOverview) -> str:
        welcome = self.welcome_page(obj)
        return serialize(welcome).get_siteName(welcome)

    def get_backgroundImageUrl(self, obj: CharacterOverview) -> str:
        welcome = self.welcome_page(obj)
        return serialize(welcome).get_backgroundImageUrl(welcome)


class ChooseCharacterModelSerializer(PageModelSerializer):
    characterType = serializers.SerializerMethodField()
    characterImageUrl = serializers.SerializerMethodField()
    backgroundImageUrl = serializers.SerializerMethodField()

    class Meta:
        model = ChooseCharacter
        fields = [
            "id",
            "title",
            "characterType",
            "name",
            "characterImageUrl",
            "backgroundImageUrl",
            "children",
            "selfUrl",
        ]
        depth = 1

    def get_characterType(self, obj: ChooseCharacter) -> str:
        return obj.character_type if obj.character_type else ""

    def get_characterImageUrl(self, obj: ChooseCharacter) -> str:
        return absolute_url(obj.character_image.file.url) if obj.character_image else ""

    def get_backgroundImageUrl(self, obj: ChooseCharacter) -> str:
        welcome = self.welcome_page(obj)
        return serialize(welcome).get_backgroundImageUrl(welcome)


class IntroSearchAndCollectModelSerializer(PageModelSerializer):
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = IntroSearchAndCollect
        fields = [
            "id",
            "title",
            "heading",
            "description",
            "imageUrl",
            "children",
            "selfUrl",
        ]
        depth = 1

    def get_imageUrl(self, obj: IntroSearchAndCollect) -> str:
        return absolute_url(obj.image.file.url) if obj.image else ""


class PhotographyScreenModelSerializer(PageModelSerializer):
    class Meta:
        model = PhotographyScreen
        fields = [
            "id",
            "title",
            "heading",
            "description",
            "children",
            "selfUrl",
        ]
        depth = 1


class YourCollectionModelSerializer(PageModelSerializer):
    imageDescriptions = serializers.SerializerMethodField()

    class Meta:
        model = YourCollection
        fields = [
            "id",
            "title",
            "heading",
            "imageDescriptions",
            "selfUrl",
        ]
        depth = 1

    def get_imageDescriptions(self, obj: YourCollection) -> list:
        return obj.image_descriptions.all().values_list("description", flat=True)
