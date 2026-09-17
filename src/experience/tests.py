import json

from django.test import TestCase
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
