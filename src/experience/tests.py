import json
import re
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import get_script_prefix, reverse
from rest_framework.renderers import JSONRenderer
from wagtail.models import Page

from .flow_links import Flow, describe_flow_link_problem, describe_move_problem
from .models import (
    ChooseCharacter,
    ChooseOption,
    Ending,
    FlowLink,
    Insight,
    Introduction,
    Photo,
)
from .page_tree_listing import TreeExplorableIndexView
from .serializers import FlowLinkModelSerializer


class FlowLinkTests(TestCase):
    def setUp(self):
        self.root = Page.objects.get(depth=2)
        self.character = ChooseCharacter(title="Artist")
        self.root.add_child(instance=self.character)
        self.introduction = Introduction(title="Introduction")
        self.character.add_child(instance=self.introduction)
        self.choice = ChooseOption(title="Choice")
        self.introduction.add_child(instance=self.choice)
        self.photo = Photo(title="Photo")
        self.choice.add_child(instance=self.photo)
        self.insight = Insight(title="Insight")
        self.choice.add_child(instance=self.insight)
        self.ending = Ending(title="Ending")
        self.photo.add_child(instance=self.ending)

        self.other_character = ChooseCharacter(title="Janitor")
        self.root.add_child(instance=self.other_character)
        self.other_introduction = Introduction(title="Other introduction")
        self.other_character.add_child(instance=self.other_introduction)
        self.other_insight = Insight(title="Other insight")
        self.other_introduction.add_child(instance=self.other_insight)

    def add_link(self, parent, target):
        link = FlowLink(title="Continue", target=target)
        parent.add_child(instance=link)
        return link

    def problem_of(self, link):
        return describe_flow_link_problem(link, Flow())

    def test_link_to_published_page_in_same_character_is_followable(self):
        self.assertIsNone(self.problem_of(self.add_link(self.insight, self.ending)))

    def test_link_without_target_is_rejected(self):
        self.assertIn(
            "no target page", self.problem_of(self.add_link(self.insight, None))
        )

    def test_link_to_unpublished_target_is_rejected(self):
        self.ending.live = False
        self.ending.save()
        link = self.add_link(self.insight, self.ending)
        self.assertIn("not published", self.problem_of(link))

    def test_link_to_other_character_is_rejected(self):
        link = self.add_link(self.insight, self.other_insight)
        self.assertIn("different character", self.problem_of(link))

    def test_link_that_loops_back_to_itself_is_rejected(self):
        link = self.add_link(self.insight, self.choice)
        self.assertIn("leads back to this link", self.problem_of(link))

    def test_serializer_exposes_the_target_translation_key(self):
        link = self.add_link(self.insight, self.ending)
        rendered = json.loads(JSONRenderer().render(FlowLinkModelSerializer(link).data))
        self.assertEqual(
            rendered["targetTranslationKey"], str(self.ending.translation_key)
        )
        self.assertEqual(rendered["children"], [])

    def test_moving_a_target_to_another_character_is_rejected(self):
        self.add_link(self.insight, self.ending)
        problem = describe_move_problem(self.ending, self.other_insight)
        self.assertIn("different character", problem)

    def test_moving_a_link_to_another_character_is_rejected(self):
        self.add_link(self.insight, self.ending)
        problem = describe_move_problem(self.insight, self.other_introduction)
        self.assertIn("different character", problem)

    def test_moving_a_page_that_would_close_a_loop_is_rejected(self):
        self.add_link(self.insight, self.ending)
        problem = describe_move_problem(self.insight, self.ending)
        self.assertIn("leads back to this link", problem)

    def test_move_within_the_same_character_is_allowed(self):
        self.add_link(self.insight, self.ending)
        spare = Insight(title="Spare")
        self.ending.add_child(instance=spare)
        self.assertIsNone(describe_move_problem(spare, self.photo))

    def test_a_link_that_is_already_broken_does_not_block_unrelated_moves(self):
        self.add_link(self.insight, None)
        spare = Insight(title="Spare")
        self.ending.add_child(instance=spare)
        self.assertIsNone(describe_move_problem(spare, self.photo))

    def test_moving_an_unpublished_page_does_not_block(self):
        self.add_link(self.insight, self.ending)
        draft = Insight(title="Draft", live=False)
        self.ending.add_child(instance=draft)
        self.assertIsNone(describe_move_problem(draft, self.photo))


class PageExplorerTreeTests(TestCase):
    def setUp(self):
        self.root = Page.objects.get(depth=2)
        self.character = ChooseCharacter(title="Artist")
        self.root.add_child(instance=self.character)
        self.introduction = Introduction(title="Introduction")
        self.character.add_child(instance=self.introduction)
        self.choice = ChooseOption(title="Choice")
        self.introduction.add_child(instance=self.choice)
        self.photo = Photo(title="Photo")
        self.choice.add_child(instance=self.photo)

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
        listed = self.titles_listed(self.explore(self.character, tree_depth=1))
        self.assertEqual(listed, ["Introduction"])

    def test_tree_depth_lists_descendants_down_to_that_depth(self):
        listed = self.titles_listed(self.explore(self.character, tree_depth=3))
        self.assertEqual(listed, ["Introduction", "Choice", "Photo"])

    def test_descendants_are_listed_in_depth_first_order(self):
        insight = Insight(title="Insight")
        self.choice.add_child(instance=insight)
        ending = Ending(title="Ending")
        self.photo.add_child(instance=ending)
        listed = self.titles_listed(self.explore(self.character, tree_depth=10))
        self.assertEqual(
            listed, ["Introduction", "Choice", "Photo", "Ending", "Insight"]
        )

    def test_rows_are_indented_by_distance_below_the_explored_page(self):
        response = self.explore(self.character, tree_depth=3)
        self.assertContains(response, "padding-inline-start: 1rem")
        self.assertContains(response, "padding-inline-start: 2rem")

    def test_chosen_depth_is_remembered_for_the_session(self):
        self.explore(self.character, tree_depth=2)
        listed = self.titles_listed(self.explore(self.character))
        self.assertEqual(listed, ["Introduction", "Choice"])

    def test_unknown_depth_falls_back_to_the_configured_default(self):
        listed = self.titles_listed(self.explore(self.character, tree_depth="banana"))
        self.assertEqual(listed, ["Introduction", "Choice", "Photo"])

    def test_explicit_ordering_falls_back_to_the_flat_listing(self):
        response = self.explore(self.character, tree_depth=3, ordering="title")
        self.assertEqual(self.titles_listed(response), ["Introduction"])
        self.assertNotContains(response, "padding-inline-start")

    def test_searching_falls_back_to_the_flat_listing(self):
        response = self.explore(self.character, tree_depth=3, q="Photo")
        self.assertNotContains(response, "padding-inline-start")

    def paginated_listing(self, page, **params):
        """Force pagination so the "select all in listing" button has a reason to render."""
        with patch.object(TreeExplorableIndexView, "paginate_by", 1):
            return self.explore(page, **params)

    def test_select_all_in_listing_is_withheld_in_tree_mode(self):
        response = self.paginated_listing(self.character, tree_depth=3)
        self.assertNotContains(response, "Select all pages in listing")
        # The per-row checkboxes stay usable, so their action buttons must survive.
        self.assertContains(response, "bulk-actions-buttons")

    def test_select_all_in_listing_is_offered_in_the_flat_listing(self):
        self.choice.add_child(instance=Insight(title="Insight"))
        response = self.paginated_listing(self.choice, tree_depth=1)
        self.assertContains(response, "Select all pages in listing")

    def test_rows_carry_the_depth_and_identity_the_collapse_script_walks(self):
        response = self.explore(self.character, tree_depth=3)
        self.assertContains(response, f'data-tree-listing="{self.character.id}"')
        self.assertContains(response, 'data-tree-depth="1"')
        self.assertContains(response, 'data-tree-depth="3"')
        self.assertContains(response, f'data-tree-page="{self.photo.id}"')

    def test_only_pages_with_listed_children_get_a_collapse_toggle(self):
        response = self.explore(self.character, tree_depth=3)
        # Introduction and Choice each have a child on screen; Photo, the deepest row, does not.
        self.assertEqual(response.content.decode().count("data-tree-toggle"), 2)

    def test_pages_whose_children_fall_outside_the_depth_get_no_toggle(self):
        response = self.explore(self.character, tree_depth=1)
        self.assertNotContains(response, "data-tree-toggle")

    def header_html(self, response):
        html = response.content.decode()
        start = html.index('id="w-slim-header-buttons"')
        return html[start : html.index("</nav>", start)]

    def body_html(self, response):
        html = response.content.decode()
        return html[html.index('id="listing-results"') :]

    def test_expand_and_collapse_all_buttons_are_offered_in_tree_mode(self):
        response = self.explore(self.character, tree_depth=3)
        self.assertIn("data-tree-expand-all", self.body_html(response))
        self.assertIn("data-tree-collapse-all", self.body_html(response))

    def test_expand_and_collapse_all_buttons_are_withheld_from_the_flat_listing(self):
        response = self.explore(self.character, tree_depth=1)
        self.assertNotContains(response, "data-tree-expand-all")
        self.assertNotContains(response, "data-tree-collapse-all")

    def test_depth_dropdown_is_offered_in_the_listing_body(self):
        response = self.explore(self.character, tree_depth=3)
        self.assertIn("Tree view: 3 levels", self.body_html(response))

    def test_depth_dropdown_stays_available_in_the_flat_listing(self):
        # Otherwise there would be no way back into tree mode once it is switched off.
        response = self.explore(self.character, tree_depth=1)
        self.assertIn("Tree view: off", self.body_html(response))

    def test_depth_dropdown_is_withheld_while_searching(self):
        response = self.explore(self.character, tree_depth=3, q="Photo")
        self.assertNotContains(response, "Tree view:")

    def test_toolbar_buttons_carry_the_classes_that_size_their_icons(self):
        # Wagtail has no global icon size rule, so a button missing these renders its icon
        # at the browser's default SVG size.
        response = self.explore(self.character, tree_depth=3)
        for markup in re.findall(
            r"<button[^>]*data-tree-(?:expand|collapse)-all[^>]*>",
            self.body_html(response),
        ):
            self.assertIn("button--icon", markup)
            self.assertRegex(markup, r'class="[^"]*\bbutton\b')

    def test_tree_controls_no_longer_crowd_the_header(self):
        response = self.explore(self.character, tree_depth=3)
        header = self.header_html(response)
        self.assertNotIn("Tree view:", header)
        self.assertNotIn("data-tree-expand-all", header)
        self.assertNotIn("data-tree-collapse-all", header)
