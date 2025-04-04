from django.db import models
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class CustomImage(AbstractImage):
    api_upload = models.BooleanField(default=False)

    admin_form_fields = Image.admin_form_fields

    def get_upload_to(self, filename):
        return ("api_upload/" + super().get_upload_to(filename) if self.api_upload
                else super().get_upload_to(filename))


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

    def get_upload_to(self, filename):
        return ("api_upload/" + super().get_upload_to(filename) if self.image.api_upload
                else super().get_upload_to(filename))
