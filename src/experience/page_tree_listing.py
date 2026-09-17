"""A page explorer that lists descendants as an indented tree.

Wagtail's explorer lists direct children only, so following this project's narrative flow
costs one page load per level and never shows the shape of a branch. Wagtail offers no hook
for listing columns, so the indentation needs its own view; ``apps.ExperienceConfig`` points
the built-in page viewset at it.

Tree mode steps aside whenever the listing means something other than "this subtree":
searching and filtering already return whole-tree results, and an explicit column sort asks
for an order that indentation would contradict.
"""

from django.conf import settings
from django.utils.functional import cached_property
from wagtail.admin.ui.tables.pages import PageTable, PageTitleColumn
from wagtail.admin.views.pages.listing import ExplorableIndexView
from wagtail.admin.widgets.button import Button, ButtonWithDropdown, HeaderButton
from wagtail.models import Page
from wagtail.permissions import page_permission_policy

SESSION_KEY = "page_explorer_tree_depth"

CHILDREN_ONLY = 1

# Copied from the dropdown Wagtail builds in WagtailAdminTemplateMixin.get_header_buttons, so
# the depth menu stays anchored to its toggle when the breadcrumbs expand.
DROPDOWN_ATTRS = {
    "data-action": (
        "w-breadcrumbs:opened@document->w-dropdown#hide "
        "w-breadcrumbs:closed@document->w-dropdown#hide"
    )
}


def depth_choices():
    return getattr(settings, "PAGE_EXPLORER_TREE_DEPTH_CHOICES", [CHILDREN_ONLY])


def default_depth():
    return getattr(settings, "PAGE_EXPLORER_TREE_DEPTH", CHILDREN_ONLY)


def expandable_page_ids(pages):
    """Ids of listed pages that have at least one of their own children listed below them.

    Only those rows get a collapse toggle: a page whose children fall outside the depth limit,
    onto the next pagination page, or outside the user's permissions has nothing to collapse.
    """
    parent_paths = {page.path[: -Page.steplen] for page in pages}
    return {page.id for page in pages if page.path in parent_paths}


def describe_depth(depth):
    if depth == CHILDREN_ONLY:
        return "Tree view: off"
    return f"Tree view: {depth} levels"


class HeaderActionButton(HeaderButton):
    """A header button that drives the collapse script instead of navigating."""

    template_name = "experience/explorer/_header_action_button.html"


class TreePageTable(PageTable):
    """Carries the row metadata the collapse script walks: depth, identity and expandability."""

    def __init__(
        self, *args, base_depth=None, expandable_page_ids=frozenset(), **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.base_depth = base_depth
        self.expandable_page_ids = expandable_page_ids

    def get_row_attrs(self, instance):
        attrs = super().get_row_attrs(instance)
        if self.base_depth is not None:
            attrs["data-tree-depth"] = instance.depth - self.base_depth
            attrs["data-tree-page"] = instance.id
        return attrs

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        context["expandable_page_ids"] = self.expandable_page_ids
        return context


class TreeDepthColumn(PageTitleColumn):
    """The title column, indented by how far the page sits below the explored parent."""

    cell_template_name = "experience/explorer/_tree_page_title_cell.html"

    def __init__(self, *args, base_depth, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_depth = base_depth

    def get_cell_context_data(self, instance, parent_context):
        context = super().get_cell_context_data(instance, parent_context)
        # PageTitleColumn reassigns parent_context's "parent_page" to the search-result parent,
        # so the explored parent's depth has to come from the column itself.
        context["indent_level"] = max(0, instance.depth - self.base_depth - 1)
        context["is_expandable"] = instance.id in parent_context.get(
            "expandable_page_ids", ()
        )
        return context


class TreeExplorableIndexView(ExplorableIndexView):
    # The bulk actions footer lives in the full page template, not the results partial.
    template_name = "experience/explorer/tree_index.html"
    table_class = TreePageTable

    @cached_property
    def tree_depth(self):
        requested = self.request.GET.get("tree_depth")
        choices = depth_choices()
        for choice in choices:
            if requested == str(choice):
                self.request.session[SESSION_KEY] = choice
                return choice
        remembered = self.request.session.get(SESSION_KEY)
        if remembered in choices:
            return remembered
        return default_depth()

    @cached_property
    def tree_mode(self):
        return (
            self.tree_depth > CHILDREN_ONLY
            and not self.is_searching
            and not self.is_filtering
            and not self.is_explicitly_ordered
        )

    def get_ordering(self):
        if self.tree_mode:
            # Leaving the ordering unset keeps the path ordering applied in get_base_queryset,
            # and keeps show_ordering_column false so drag-reordering cannot fight the tree.
            return None
        return super().get_ordering()

    def get_base_queryset(self):
        if not self.tree_mode:
            return super().get_base_queryset()

        pages = self.model._default_manager.descendant_of(self.parent_page).filter(
            depth__lte=self.parent_page.depth + self.tree_depth
        )
        pages = pages.filter(
            pk__in=page_permission_policy.explorable_instances(
                self.request.user
            ).values_list("pk", flat=True)
        )
        pages = self.annotate_queryset(pages)
        # Materialised paths are prefix encoded, so ordering by path is a depth-first walk.
        # Wagtail orders by "-pk" behind our back unless the queryset reports itself ordered.
        return pages.order_by("path")

    @cached_property
    def explorable_columns(self):
        columns = super().explorable_columns
        if not self.tree_mode:
            return columns
        return [
            TreeDepthColumn(
                column.name,
                label=column.label,
                sort_key=column.sort_key,
                classname=column.classname,
                base_depth=self.parent_page.depth,
            )
            if column.name == "title"
            else column
            for column in columns
        ]

    def get_table(self, object_list):
        if not self.tree_mode:
            return super().get_table(object_list)
        rows = list(object_list)
        return self.table_class(
            self.explorable_columns,
            rows,
            base_depth=self.parent_page.depth,
            expandable_page_ids=expandable_page_ids(rows),
            attrs={"data-tree-listing": self.parent_page.id},
            **self.get_table_kwargs(),
        )

    @cached_property
    def depth_button(self):
        return ButtonWithDropdown(
            label=describe_depth(self.tree_depth),
            buttons=[
                Button(
                    describe_depth(choice), url=f"?tree_depth={choice}", priority=index
                )
                for index, choice in enumerate(depth_choices())
            ],
            icon_name="list-ul",
            classname="w-h-slim-header",
            attrs=DROPDOWN_ATTRS,
            priority=50,
        )

    @cached_property
    def collapse_buttons(self):
        if not self.tree_mode:
            return []
        return [
            HeaderActionButton(
                "Expand all",
                classname="button-secondary",
                icon_name="collapse-down",
                attrs={"data-tree-expand-all": True},
                priority=60,
            ),
            HeaderActionButton(
                "Collapse all",
                classname="button-secondary",
                icon_name="expand-right",
                attrs={"data-tree-collapse-all": True},
                priority=70,
            ),
        ]

    @cached_property
    def header_buttons(self):
        return [*super().header_buttons, self.depth_button, *self.collapse_buttons]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tree_mode"] = self.tree_mode
        return context
