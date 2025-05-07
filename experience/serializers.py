from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import CharacterOverview, ChooseCharacter, Welcome


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
        return serializer.data if serializer.data else []

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
        return serializer.data if serializer.data else []

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

    def get_selfUrl(self, obj: ChooseCharacter) -> str:
        return (
            settings.WAGTAILADMIN_BASE_URL
            + settings.API_BASE_URL
            + "/choose-character/"
            + str(obj.id)
        )
