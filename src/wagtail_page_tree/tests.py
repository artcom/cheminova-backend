import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import get_script_prefix, reverse
from wagtail.models import Page

from .listing import TreeExplorableIndexView


def add_page(parent, title):
    """A plain page of the given title under the given parent.

    The listing treats every page the same, so the tests need no page types of their own.
    """
    page = Page(title=title)
    parent.add_child(instance=page)
    return page


@override_settings(
    # Pinned so the suite tests the app rather than whatever the host project configures.
    PAGE_EXPLORER_TREE_DEPTH=3,
    PAGE_EXPLORER_TREE_DEPTH_CHOICES=[1, 2, 3, 5, 10],
)
class PageExplorerTreeTests(TestCase):
    def setUp(self):
        self.root = Page.objects.get(depth=2)
        self.section = add_page(self.root, "Section")
        self.chapter = add_page(self.section, "Chapter")
        self.topic = add_page(self.chapter, "Topic")
        self.detail = add_page(self.topic, "Detail")

        self.editor = get_user_model().objects.create_superuser(
            username="editor", email="editor@example.com", password="password"
        )
        self.client.force_login(self.editor)

    def explore(self, page, **params):
        # Deployments mount the CMS under a script prefix, which reverse() includes but the
        # test client resolves without.
        url = reverse("wagtailadmin_explore", args=[page.id]).removeprefix(
            get_script_prefix().removesuffix("/")
        )
        return self.client.get(url, params)

    def titles_listed(self, response):
        return [page.title for page in response.context["object_list"]]

    def test_children_only_depth_lists_direct_children_alone(self):
        listed = self.titles_listed(self.explore(self.section, tree_depth=1))
        self.assertEqual(listed, ["Chapter"])

    def test_tree_depth_lists_descendants_down_to_that_depth(self):
        listed = self.titles_listed(self.explore(self.section, tree_depth=3))
        self.assertEqual(listed, ["Chapter", "Topic", "Detail"])

    def test_descendants_are_listed_in_depth_first_order(self):
        add_page(self.topic, "Aside")
        add_page(self.detail, "Footnote")
        listed = self.titles_listed(self.explore(self.section, tree_depth=10))
        self.assertEqual(listed, ["Chapter", "Topic", "Detail", "Footnote", "Aside"])

    def test_rows_are_indented_by_distance_below_the_explored_page(self):
        response = self.explore(self.section, tree_depth=3)
        self.assertContains(response, "padding-inline-start: 1rem")
        self.assertContains(response, "padding-inline-start: 2rem")

    def test_chosen_depth_is_remembered_for_the_session(self):
        self.explore(self.section, tree_depth=2)
        listed = self.titles_listed(self.explore(self.section))
        self.assertEqual(listed, ["Chapter", "Topic"])

    def test_unknown_depth_falls_back_to_the_configured_default(self):
        listed = self.titles_listed(self.explore(self.section, tree_depth="banana"))
        self.assertEqual(listed, ["Chapter", "Topic", "Detail"])

    def test_explicit_ordering_falls_back_to_the_flat_listing(self):
        response = self.explore(self.section, tree_depth=3, ordering="title")
        self.assertEqual(self.titles_listed(response), ["Chapter"])
        self.assertNotContains(response, "padding-inline-start")

    def test_searching_falls_back_to_the_flat_listing(self):
        response = self.explore(self.section, tree_depth=3, q="Detail")
        self.assertNotContains(response, "padding-inline-start")

    def paginated_listing(self, page, **params):
        """Force pagination so the "select all in listing" button has a reason to render."""
        with patch.object(TreeExplorableIndexView, "paginate_by", 1):
            return self.explore(page, **params)

    def test_select_all_in_listing_is_withheld_in_tree_mode(self):
        response = self.paginated_listing(self.section, tree_depth=3)
        self.assertNotContains(response, "Select all pages in listing")
        # The per-row checkboxes stay usable, so their action buttons must survive.
        self.assertContains(response, "bulk-actions-buttons")

    def test_select_all_in_listing_is_offered_in_the_flat_listing(self):
        add_page(self.topic, "Aside")
        response = self.paginated_listing(self.topic, tree_depth=1)
        self.assertContains(response, "Select all pages in listing")

    def test_rows_carry_the_depth_and_identity_the_collapse_script_walks(self):
        response = self.explore(self.section, tree_depth=3)
        self.assertContains(response, f'data-tree-listing="{self.section.id}"')
        self.assertContains(response, 'data-tree-depth="1"')
        self.assertContains(response, 'data-tree-depth="3"')
        self.assertContains(response, f'data-tree-page="{self.detail.id}"')

    def test_only_pages_with_listed_children_get_a_collapse_toggle(self):
        response = self.explore(self.section, tree_depth=3)
        # Chapter and Topic each have a child on screen; Detail, the deepest row, does not.
        self.assertEqual(response.content.decode().count("data-tree-toggle"), 2)

    def test_pages_whose_children_fall_outside_the_depth_get_no_toggle(self):
        response = self.explore(self.section, tree_depth=1)
        self.assertNotContains(response, "data-tree-toggle")

    def header_html(self, response):
        html = response.content.decode()
        start = html.index('id="w-slim-header-buttons"')
        return html[start : html.index("</nav>", start)]

    def body_html(self, response):
        html = response.content.decode()
        return html[html.index('id="listing-results"') :]

    def test_expand_and_collapse_all_buttons_are_offered_in_tree_mode(self):
        response = self.explore(self.section, tree_depth=3)
        self.assertIn("data-tree-expand-all", self.body_html(response))
        self.assertIn("data-tree-collapse-all", self.body_html(response))

    def test_expand_and_collapse_all_buttons_are_withheld_from_the_flat_listing(self):
        response = self.explore(self.section, tree_depth=1)
        self.assertNotContains(response, "data-tree-expand-all")
        self.assertNotContains(response, "data-tree-collapse-all")

    def test_depth_dropdown_is_offered_in_the_listing_body(self):
        response = self.explore(self.section, tree_depth=3)
        self.assertIn("Tree view: 3 levels", self.body_html(response))

    def test_depth_dropdown_stays_available_in_the_flat_listing(self):
        # Otherwise there would be no way back into tree mode once it is switched off.
        response = self.explore(self.section, tree_depth=1)
        self.assertIn("Tree view: off", self.body_html(response))

    def test_depth_dropdown_is_withheld_while_searching(self):
        response = self.explore(self.section, tree_depth=3, q="Detail")
        self.assertNotContains(response, "Tree view:")

    def test_toolbar_buttons_carry_the_classes_that_size_their_icons(self):
        # Wagtail has no global icon size rule, so a button missing these renders its icon
        # at the browser's default SVG size.
        response = self.explore(self.section, tree_depth=3)
        for markup in re.findall(
            r"<button[^>]*data-tree-(?:expand|collapse)-all[^>]*>",
            self.body_html(response),
        ):
            self.assertIn("button--icon", markup)
            self.assertRegex(markup, r'class="[^"]*\bbutton\b')

    def test_tree_controls_no_longer_crowd_the_header(self):
        response = self.explore(self.section, tree_depth=3)
        header = self.header_html(response)
        self.assertNotIn("Tree view:", header)
        self.assertNotIn("data-tree-expand-all", header)
        self.assertNotIn("data-tree-collapse-all", header)
