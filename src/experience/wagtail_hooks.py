from django.contrib import messages
from django.contrib.auth.models import Permission
from django.shortcuts import redirect
from wagtail import hooks

from .models import ChooseOption
from .page_flow import ALLOWED_SUBPAGES


@hooks.register("register_permissions")
def register_permissions():
    return Permission.objects.filter(
        codename__in=[
            "choose_character.edit_restricted",
            "introduction.edit_restricted",
            "insight.edit_restricted",
        ],
    )


@hooks.register("before_publish_page")
def require_every_option_under_choice(request, page):
    if not isinstance(page.specific, ChooseOption):
        return None
    published = {
        child.specific_class.__name__ for child in page.get_children().live().specific()
    }
    missing = [
        name for name in ALLOWED_SUBPAGES["ChooseOption"] if name not in published
    ]
    if not missing:
        return None
    messages.error(
        request,
        f"“{page.title}” needs a published child page of each type before it can be "
        f"published. Missing or unpublished: {', '.join(missing)}.",
    )
    return redirect("wagtailadmin_pages:edit", page.id)
