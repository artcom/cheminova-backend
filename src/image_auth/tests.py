from io import BytesIO
from pathlib import Path

import PIL.Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from wagtail.images import get_image_model
from wagtail.models import Collection, Page, ReferenceIndex

from experience.models import Character, Characters, Welcome


def get_test_image_file(filename="test.png", colour="white", size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new("RGBA", size, colour)
    image.save(f, "PNG")
    return ImageFile(f, name=filename)


class ImageAuthTests(APITestCase):
    def setUp(self):
        self.image_auth_url = reverse("image-permissions")
        Image = get_image_model()
        root_page = Page.objects.get(slug="root")
        self.published_image = Image.objects.create(
            title="Test Image", file=get_test_image_file(filename="test.png")
        )
        self.unpublished_image = Image.objects.create(
            title="Test Image Not Live",
            file=get_test_image_file(filename="test-not-live.png"),
        )
        self.approved_image_collection = Collection.objects.create(
            name="Approved Collection", depth=2, path="00010001"
        )
        self.no_approved_image_collection = Collection.objects.create(
            name="No Approved Collection", depth=2, path="00010002"
        )
        self.characters = Characters(title="Test Characters")
        self.character = Character(
            name="Test Character",
            slug="test-character",
            page=self.characters,
            approved_collection=self.approved_image_collection,
            not_approved_collection=self.no_approved_image_collection,
        )
        root_page.add_child(instance=self.characters)
        self.character.save()
        self.approved_image = Image.objects.create(
            title="Test Image Approved",
            file=get_test_image_file(filename="test-approved.png"),
            collection=self.approved_image_collection,
        )
        self.not_approved_image = Image.objects.create(
            title="Test Image Not Approved",
            file=get_test_image_file(filename="test-not-approved.png"),
            collection=self.no_approved_image_collection,
        )

        self.welcome = Welcome(
            title="Welcome", slug="welcome", background_image=self.published_image
        )
        root_page.add_child(instance=self.welcome)
        revision = self.welcome.save_revision()
        self.welcome.publish(revision)
        ReferenceIndex.create_or_update_for_object(self.welcome)
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def tearDown(self):
        images = [self.published_image, self.unpublished_image]
        self.characters.delete()
        self.approved_image_collection.delete()
        self.no_approved_image_collection.delete()
        self.welcome.delete()
        for image in images:
            path = Path(settings.MEDIA_ROOT).joinpath(str(image.file))
            if path.exists():
                path.unlink()
            image.delete()

    def test_check_permissions_authenticated(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.image_auth_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_anonymous_no_original_uri_header(self):
        response = self.client.get(self.image_auth_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_permissions_anonymous_with_invalid_file_type(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}invalid/non_existent_file.jpg"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_permissions_anonymous_with_nonexistent_file(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}original_images/non_existent_file.jpg"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_permissions_anonymous_with_published_file(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.published_image.file)}"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_anonymous_with_unpublished_file(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.unpublished_image.file)}"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_permissions_anonymous_with_approved_file(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.approved_image.file)}"
            },
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_anonymous_with_not_approved_file(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.not_approved_image.file)}"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RenditionsTestCase(APITestCase):
    def setUp(self):
        self.image_auth_url = reverse("image-permissions")
        Image = get_image_model()
        self.published_image = Image.objects.create(
            title="Test Image", file=get_test_image_file(filename="test.png")
        )
        self.unpublished_image = Image.objects.create(
            title="Test Image Not Live",
            file=get_test_image_file(filename="test-not-live.png"),
        )
        root_page = Page.objects.get(slug="root")
        self.welcome = Welcome(
            title="Welcome", slug="welcome", background_image=self.published_image
        )
        root_page.add_child(instance=self.welcome)
        revision = self.welcome.save_revision()
        self.welcome.publish(revision)
        ReferenceIndex.create_or_update_for_object(self.welcome)
        self.published_rendition = self.published_image.get_rendition("width-400")
        self.unpublished_rendition = self.unpublished_image.get_rendition("width-400")

    def tearDown(self):
        images = [
            self.published_image,
            self.unpublished_image,
            self.published_rendition,
            self.unpublished_rendition,
        ]
        self.welcome.delete()
        for image in images:
            path = Path(settings.MEDIA_ROOT).joinpath(str(image.file))
            if path.exists():
                path.unlink()
            image.delete()

    def test_check_permissions_anonymous_with_nonexistent_rendition(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}images/non_existent_file.width-400.jpg"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_permissions_anonymous_with_rendition_from_published_file(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.published_rendition.file)}"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_anonymous_with_rendition_from_unpublished_file(self):
        response = self.client.get(
            self.image_auth_url,
            headers={
                "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.unpublished_rendition.file)}"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
