from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import (
    CharacterOverview,
    ChooseCharacter,
    IntroSearchAndCollect,
    Welcome,
    PhotographyScreen,
    YourCollection,
)


class WelcomeModelSerializer(serializers.ModelSerializer):
    backgroundImageUrl = serializers.SerializerMethodField()
    siteName = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    selfUrl = serializers.SerializerMethodField()

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
        return settings.WAGTAILADMIN_BASE_URL + obj.background_image.file.url

    def get_siteName(self, obj: Welcome) -> str:
        return obj.site_name if obj.site_name else ""

    def get_children(self, obj: Welcome) -> list:
        children = obj.get_children().live().specific()
        serializer = CharacterOverviewModelSerializer(children, many=True)
        children_urls = [data.get("selfUrl") for data in serializer.data]
        return children_urls if serializer.data else []

    def get_selfUrl(self, obj: Welcome) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + settings.API_BASE_URL
            + "/welcome/"
            + str(obj.id)
        )


class CharacterOverviewModelSerializer(serializers.ModelSerializer):
    charactersImageUrl = serializers.SerializerMethodField()
    backgroundImageUrl = serializers.SerializerMethodField()
    siteName = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    selfUrl = serializers.SerializerMethodField()

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
        return settings.WAGTAILADMIN_BASE_URL + obj.characters_image.file.url

    def get_siteName(self, obj: CharacterOverview) -> str:
        return Welcome.objects.get(id=obj.get_parent().id).site_name

    def get_backgroundImageUrl(self, obj: CharacterOverview) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + Welcome.objects.get(id=obj.get_parent().id).background_image.file.url
        )

    def get_children(self, obj: CharacterOverview) -> list:
        children = obj.get_children().live().specific()
        serializer = ChooseCharacterModelSerializer(children, many=True)
        children_urls = [data.get("selfUrl") for data in serializer.data]
        return children_urls if serializer.data else []

    def get_selfUrl(self, obj: CharacterOverview) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + settings.API_BASE_URL
            + "/character-overview/"
            + str(obj.id)
        )


class ChooseCharacterModelSerializer(serializers.ModelSerializer):
    characterType = serializers.SerializerMethodField()
    characterImageUrl = serializers.SerializerMethodField()
    backgroundImageUrl = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    selfUrl = serializers.SerializerMethodField()

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
        return (
            settings.WAGTAILADMIN_BASE_URL + obj.character_image.file.url
            if obj.character_image
            else ""
        )

    def get_backgroundImageUrl(self, obj: ChooseCharacter) -> str:
        welcome_ancestor = next(
            (
                ancestor
                for ancestor in obj.get_ancestors()
                if ancestor.get_content_type().model == "welcome"
            ),
            None,
        )
        return (
            settings.WAGTAILADMIN_BASE_URL
            + Welcome.objects.get(id=welcome_ancestor.id).background_image.file.url
            if welcome_ancestor
            else ""
        )

    def get_children(self, obj: ChooseCharacter) -> list:
        children = obj.get_children().live().specific()
        serializer = IntroSearchAndCollectModelSerializer(children, many=True)
        children_urls = [data.get("selfUrl") for data in serializer.data]
        return children_urls if serializer.data else []

    def get_selfUrl(self, obj: ChooseCharacter) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + settings.API_BASE_URL
            + "/choose-character/"
            + str(obj.id)
        )


class IntroSearchAndCollectModelSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    selfUrl = serializers.SerializerMethodField()

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
        return settings.WAGTAILADMIN_BASE_URL + obj.image.file.url if obj.image else ""

    def get_children(self, obj: IntroSearchAndCollect) -> list:
        children = obj.get_children().live().specific()
        serializer = PhotographyScreenModelSerializer(children, many=True)
        children_urls = [data.get("selfUrl") for data in serializer.data]
        return children_urls if serializer.data else []

    def get_selfUrl(self, obj: IntroSearchAndCollect) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + settings.API_BASE_URL
            + "/intro-search-and-collect/"
            + str(obj.id)
        )


class PhotographyScreenModelSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    selfUrl = serializers.SerializerMethodField()

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

    def get_children(self, obj: PhotographyScreen) -> list:
        children = obj.get_children().live().specific()
        serializer = YourCollectionModelSerializer(children, many=True)
        children_urls = [data.get("selfUrl") for data in serializer.data]
        return children_urls if serializer.data else []

    def get_selfUrl(self, obj: PhotographyScreen) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + settings.API_BASE_URL
            + "/photography-screen/"
            + str(obj.id)
        )


class YourCollectionModelSerializer(serializers.ModelSerializer):
    imageDescriptions = serializers.SerializerMethodField()
    selfUrl = serializers.SerializerMethodField()

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
        return [
            image_description
            for image_description in [
                getattr(obj, f"image_description_{i}") for i in range(1, 4)
            ]
        ]

    def get_selfUrl(self, obj: YourCollection) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + settings.API_BASE_URL
            + "/your-collection/"
            + str(obj.id)
        )
