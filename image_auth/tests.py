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


def get_test_image_file(filename="test.png", colour="white", size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new("RGBA", size, colour)
    image.save(f, "PNG")
    return ImageFile(f, name=filename)


class ImageAuthTests(APITestCase):
    def setUp(self):
        self.image_url = reverse("image-permissions")
        self.Image = get_image_model()
        self.image = self.Image.objects.create(
            title="Test Image", file=get_test_image_file(filename="test.png"))
        self.user = User.objects.create_user(
            username="testuser", password="testpassword")

    def tearDown(self):
        image = Path(settings.MEDIA_ROOT).joinpath(str(self.image.file))
        if image.exists():
            image.unlink()
        self.image.delete()

    def test_check_permissions_authenticated(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.image_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_anonymous_no_original_uri_header(self):
        response = self.client.get(self.image_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_permissions_anonymous_with_invalid_file_type(self):
        response = self.client.get(self.image_url, headers={
            "X-Original-Uri": f"{settings.MEDIA_URL}invalid/non_existent_file.jpg"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_permissions_anonymous_with_nonexistent_file(self):
        response = self.client.get(self.image_url, headers={
            "X-Original-Uri": f"{settings.MEDIA_URL}original_images/non_existent_file.jpg"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_permissions_anonymous_with_hidden_file(self):
        self.image.hidden = True
        self.image.save()
        response = self.client.get(self.image_url, headers={
            "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.image.file)}"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_permissions_anonymous_with_visible_file(self):
        self.image.hidden = False
        self.image.save()
        response = self.client.get(self.image_url, headers={
            "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.image.file)}"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RenditionsTestCase(APITestCase):
    def setUp(self):
        self.image_url = reverse("image-permissions")
        self.Image = get_image_model()
        self.image = self.Image.objects.create(
            title="Test Image", file=get_test_image_file(filename="test.png"))
        self.rendition = self.image.get_rendition("width-400")

    def tearDown(self):
        image = Path(settings.MEDIA_ROOT).joinpath(str(self.image.file))
        if image.exists():
            image.unlink()
        self.image.delete()
        rendition = Path(settings.MEDIA_ROOT).joinpath(str(self.rendition.file))
        if rendition.exists():
            rendition.unlink()
        self.rendition.delete()

    def test_check_permissions_anonymous_with_nonexistent_rendition(self):
        response = self.client.get(self.image_url, headers={
            "X-Original-Uri": f"{settings.MEDIA_URL}images/non_existent_file.width-400.jpg"
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_permissions_anonymous_with_rendition_from_hidden_file(self):
        self.image.hidden = True
        self.image.save()
        response = self.client.get(self.image_url, headers={
            "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.rendition.file)}"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_permissions_anonymous_with_rendition_from_visible_file(self):
        self.image.hidden = False
        self.image.save()
        response = self.client.get(self.image_url, headers={
            "X-Original-Uri": f"{settings.MEDIA_URL}{str(self.rendition.file)}"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
