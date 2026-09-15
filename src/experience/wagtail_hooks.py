from django.contrib import messages
from django.contrib.auth.models import Permission
from django.shortcuts import redirect
from wagtail import hooks

from .flow_links import Flow, describe_flow_link_problem, describe_move_problem
from .models import ChooseOption, FlowLink
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


@hooks.register("before_publish_page")
def require_followable_flow_link(request, page):
    if not isinstance(page.specific, FlowLink):
        return None
    problem = describe_flow_link_problem(page.specific, Flow())
    if not problem:
        return None
    messages.error(request, f"“{page.title}” cannot be published because {problem}.")
    return redirect("wagtailadmin_pages:edit", page.id)


@hooks.register("before_move_page")
def keep_flow_links_followable_across_moves(request, page_to_move, destination):
    problem = describe_move_problem(page_to_move, destination)
    if not problem:
        return None
    messages.error(
        request,
        f"“{page_to_move.title}” cannot be moved under “{destination.title}” because "
        f"{problem}.",
    )
    return redirect("wagtailadmin_pages:move", page_to_move.id)
