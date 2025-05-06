from django.conf import settings
from django.db import models  # noqa
from rest_framework import serializers

from .models import Welcome, CharacterOverview, ChooseCharacter


class WelcomeModelSerializer(serializers.ModelSerializer):
    backgroundImageUrl = serializers.SerializerMethodField()
    siteName = serializers.SerializerMethodField()

    class Meta:
        model = Welcome
        fields = ["id", "title", "description", "siteName", "backgroundImageUrl"]
        depth = 1

    def get_backgroundImageUrl(self, obj: Welcome) -> str:
        return settings.WAGTAILADMIN_BASE_URL + obj.background_image.file.url

    def get_siteName(self, obj: Welcome) -> str:
        return obj.site_name if obj.site_name else ""


class CharacterOverviewModelSerializer(serializers.ModelSerializer):
    charactersImageUrl = serializers.SerializerMethodField()
    backgroundImageUrl = serializers.SerializerMethodField()
    siteName = serializers.SerializerMethodField()

    class Meta:
        model = CharacterOverview
        fields = [
            "id",
            "title",
            "siteName",
            "backgroundImageUrl",
            "charactersImageUrl",
            "onboarding",
        ]
        depth = 1

    def get_charactersImageUrl(self, obj: CharacterOverview) -> str:
        return settings.WAGTAILADMIN_BASE_URL + obj.characters_image.file.url

    def get_siteName(self, obj: CharacterOverview) -> str:
        return Welcome.objects.get(id=obj.get_parent().id).site_name

    def get_backgroundImageUrl(self, obj: CharacterOverview) -> str:
        return Welcome.objects.get(id=obj.get_parent().id).background_image.file.url


class ChooseCharacterModelSerializer(serializers.ModelSerializer):
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
            Welcome.objects.get(id=welcome_ancestor.id).background_image.file.url
            if welcome_ancestor
            else ""
        )
