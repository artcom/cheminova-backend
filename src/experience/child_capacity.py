"""How many children a page may hold.

Wagtail's ``max_count_per_parent`` caps one child type per parent and is declared on the
child, so it cannot express "this parent may fork, that one may not". These rules can.
"""

from enum import Enum


class ChildCapacity(Enum):
    SINGLE_PATH = "single_path"
    ONE_PER_TYPE = "one_per_type"
    MANY = "many"


def capacity_of(parent):
    return getattr(parent.specific_class, "child_capacity", ChildCapacity.MANY)


def accepts_child(parent, child_class, moved_page=None):
    children = parent.get_children()
    if moved_page is not None:
        children = children.not_page(moved_page)
    capacity = capacity_of(parent)
    if capacity is ChildCapacity.MANY:
        return True
    if capacity is ChildCapacity.ONE_PER_TYPE:
        return not children.type(child_class).exists()
    return not children.exists()


class ChildCapacityMixin:
    child_capacity = ChildCapacity.SINGLE_PATH

    @classmethod
    def can_create_at(cls, parent):
        return super().can_create_at(parent) and accepts_child(parent, cls)

    def can_move_to(self, parent):
        return super().can_move_to(parent) and accepts_child(
            parent, self.specific_class, moved_page=self
        )
