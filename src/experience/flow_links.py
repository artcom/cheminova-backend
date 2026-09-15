"""Validation for the jumps a ``FlowLink`` introduces.

The page tree is acyclic by construction, so a ``FlowLink`` is the only way the flow can
loop. It is also the only way the flow can leave the subtree it lives in, so these rules
are what keep a visitor from carrying one character's pages under another's persona: a
link may only be published, and a page may only be moved, while every published link
still points at a page of the character it belongs to.
"""

from .models import ChooseCharacter, FlowLink


class Flow:
    """The page tree as the experience walks it."""

    def successors(self, page):
        specific = page.specific
        if isinstance(specific, FlowLink):
            return [specific.target] if specific.target_id else []
        return list(page.get_children().live().specific())

    def character_of(self, page):
        return page.get_ancestors(inclusive=True).type(ChooseCharacter).last()

    def reaches(self, start, searched_page):
        pending = [start]
        visited = set()
        while pending:
            page = pending.pop()
            if page.id == searched_page.id:
                return True
            if page.id in visited:
                continue
            visited.add(page.id)
            pending.extend(self.successors(page))
        return False


class FlowAfterMove(Flow):
    """The flow as it would be once ``moved_page`` sits under ``destination``."""

    def __init__(self, moved_page, destination):
        self.moved_page = moved_page
        self.destination = destination
        self.former_parent = moved_page.get_parent()

    def successors(self, page):
        successors = super().successors(page)
        if page.id == self.former_parent.id:
            successors = [
                successor
                for successor in successors
                if successor.id != self.moved_page.id
            ]
        if page.id == self.destination.id and self.moved_page.live:
            successors = [*successors, self.moved_page.specific]
        return successors

    def is_moving(self, page):
        return page.id == self.moved_page.id or page.is_descendant_of(self.moved_page)

    def character_of(self, page):
        if not self.is_moving(page):
            return super().character_of(page)
        character_inside_the_moved_subtree = (
            page.get_ancestors(inclusive=True)
            .descendant_of(self.moved_page, inclusive=True)
            .type(ChooseCharacter)
            .last()
        )
        return character_inside_the_moved_subtree or super().character_of(
            self.destination
        )


def describe_flow_link_problem(flow_link, flow):
    """Return why ``flow_link`` cannot be followed in ``flow``, or ``None`` when it can."""
    target = flow_link.target
    if target is None:
        return "it has no target page"
    if not target.live:
        return f"its target “{target.title}” is not published"
    if flow.character_of(target) != flow.character_of(flow_link):
        return f"its target “{target.title}” belongs to a different character"
    if flow.reaches(target, flow_link):
        return f"its target “{target.title}” leads back to this link"
    return None


def describe_move_problem(moved_page, destination):
    """Return which published link the move would break, or ``None`` when it breaks none."""
    flow = Flow()
    flow_after_move = FlowAfterMove(moved_page, destination)
    for flow_link in FlowLink.objects.live():
        if describe_flow_link_problem(flow_link, flow):
            continue
        problem = describe_flow_link_problem(flow_link, flow_after_move)
        if problem:
            return f"the flow link “{flow_link.title}” would then break: {problem}"
    return None
