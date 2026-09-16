from django.apps import AppConfig


class ExperienceConfig(AppConfig):
    name = "experience"

    def ready(self):
        """Point Wagtail's built-in page viewset at the tree explorer.

        The "Pages" sidebar item resolves to wagtailadmin_explore_root, which is wired straight
        to base_page_viewset rather than through the viewset registry, so registering a
        PageViewSet of our own would leave that URL on the stock listing. The viewset builds its
        views lazily when the URLconf is imported, which is always after this runs.
        """
        from wagtail.admin.viewsets.pages import base_page_viewset

        from .page_tree_listing import TreeExplorableIndexView

        base_page_viewset.index_view_class = TreeExplorableIndexView
