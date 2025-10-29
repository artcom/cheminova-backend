from io import BytesIO
from pathlib import Path

import PIL.Image
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.files.images import ImageFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from wagtail.images import get_image_model
from wagtail.images.models import Image
from wagtail.models import Collection, GroupCollectionPermission, Page, ReferenceIndex

from experience.models import Character, Characters, Welcome


def get_test_image_file(filename="test.png", colour="white", size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new("RGBA", size, colour)
    image.save(f, "PNG")
    return ImageFile(f, name=filename)


class ImageAuthTests(APITestCase):
    def setUp(self):
        self.image_auth_url = reverse("image-permissions")
        CustomImage = get_image_model()
        root_page = Page.objects.get(slug="root")

        # Permissions
        image_content_type = ContentType.objects.get_for_model(Image)
        add_image_permission = Permission.objects.get(
            content_type=image_content_type, codename="add_image"
        )
        change_image_permission = Permission.objects.get(
            content_type=image_content_type, codename="change_image"
        )

        # Collections
        self.root_collection = Collection.get_first_root_node()
        self.approved_image_collection = self.root_collection.add_child(
            name="Approved Collection"
        )
        self.not_approved_image_collection = self.root_collection.add_child(
            name="Not Approved Collection"
        )
        self.public_image_collection = self.root_collection.add_child(
            name="Public Collection"
        )

        # Groups
        editors_group = Group.objects.create(name="Test Editors")
        GroupCollectionPermission.objects.create(
            group=editors_group,
            collection=self.public_image_collection,
            permission=change_image_permission,
        )
        GroupCollectionPermission.objects.create(
            group=editors_group,
            collection=self.public_image_collection,
            permission=add_image_permission,
        )

        # Images
        self.approved_image = CustomImage.objects.create(
            title="Test Image Approved",
            file=get_test_image_file(filename="test-approved.png"),
            collection=self.approved_image_collection,
        )
        self.not_approved_image = CustomImage.objects.create(
            title="Test Image Not Approved",
            file=get_test_image_file(filename="test-not-approved.png"),
            collection=self.not_approved_image_collection,
        )
        self.published_image = CustomImage.objects.create(
            title="Test Image",
            file=get_test_image_file(filename="test.png"),
            collection=self.public_image_collection,
        )
        self.unpublished_image = CustomImage.objects.create(
            title="Test Image Not Live",
            file=get_test_image_file(filename="test-not-live.png"),
            collection=self.public_image_collection,
        )
        self.approved_image_rendition = self.approved_image.get_rendition("width-400")
        self.not_approved_image_rendition = self.not_approved_image.get_rendition(
            "width-400"
        )
        self.published_image_rendition = self.published_image.get_rendition("width-400")
        self.unpublished_image_rendition = self.unpublished_image.get_rendition(
            "width-400"
        )
        self.images = [
            self.approved_image,
            self.not_approved_image,
            self.approved_image_rendition,
            self.not_approved_image_rendition,
            self.published_image,
            self.unpublished_image,
            self.published_image_rendition,
            self.unpublished_image_rendition,
        ]

        # Pages
        ## Characters
        self.characters = Characters(title="Test Characters")
        self.character = Character(
            name="Test Character",
            slug="test-character",
            page=self.characters,
            approved_collection=self.approved_image_collection,
            not_approved_collection=self.not_approved_image_collection,
        )
        root_page.add_child(instance=self.characters)
        self.character.save()

        ## Welcome Page
        self.welcome = Welcome(
            title="Welcome", slug="welcome", background_image=self.published_image
        )
        root_page.add_child(instance=self.welcome)
        revision = self.welcome.save_revision()
        self.welcome.publish(revision)
        ReferenceIndex.create_or_update_for_object(self.welcome)

        # Users
        self.editor_username = "editor"
        self.editor_password = "edpassword"
        self.editor_user = User.objects.create_user(
            username=self.editor_username, password=self.editor_password
        )
        self.editor_user.groups.add(editors_group)

    def tearDown(self):
        for image in self.images:
            path = Path(settings.MEDIA_ROOT).joinpath(str(image.file))
            if path.exists():
                path.unlink()
            image.delete()

    def test_check_permissions_editor_published_file(self):
        for file in [self.published_image, self.published_image_rendition]:
            self.client.login(
                username=self.editor_username, password=self.editor_password
            )
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_editor_unpublished_file(self):
        for file in [self.unpublished_image, self.unpublished_image_rendition]:
            self.client.login(
                username=self.editor_username, password=self.editor_password
            )
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_editor_approved_file(self):
        for file in [self.approved_image, self.approved_image_rendition]:
            self.client.login(
                username=self.editor_username, password=self.editor_password
            )
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_editor_not_approved_file(self):
        for file in [self.not_approved_image, self.not_approved_image_rendition]:
            self.client.login(
                username=self.editor_username, password=self.editor_password
            )
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        for file in [self.published_image, self.published_image_rendition]:
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_anonymous_with_unpublished_file(self):
        for file in [self.unpublished_image, self.unpublished_image_rendition]:
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_permissions_anonymous_with_approved_file(self):
        for file in [self.approved_image, self.approved_image_rendition]:
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_permissions_anonymous_with_not_approved_file(self):
        for file in [self.not_approved_image, self.not_approved_image_rendition]:
            response = self.client.get(
                self.image_auth_url,
                headers={"X-Original-Uri": f"{settings.MEDIA_URL}{str(file.file)}"},
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
