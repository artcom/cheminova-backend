from django.contrib.auth.models import Permission
from wagtail import hooks


@hooks.register("register_permissions")
def register_permissions():
    return Permission.objects.filter(
        codename__in=[
            "choose_character.edit_restricted",
            "introduction.edit_restricted",
            "insight.edit_restricted",
        ],
    )
