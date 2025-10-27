from django.contrib.auth.models import Permission
from wagtail import hooks


@hooks.register("register_permissions")
def register_permissions():
    return Permission.objects.filter(
        codename__in=[
            "exploration.edit_restricted",
            "choose_character.edit_restricted",
            "introduction.edit_restricted",
        ],
    )
