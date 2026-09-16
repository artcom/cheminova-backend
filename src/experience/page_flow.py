"""Single source of truth for the page hierarchy.

Wagtail allows a parent/child relationship only when both ``subpage_types`` on the parent
and ``parent_page_types`` on the child permit it. Declaring the flow once in one direction
and deriving the other is the only way to keep the two from drifting apart.
"""

ROOT_PAGE_TYPES = ["Characters", "WelcomeLanguage"]

OPTION_PAGE_TYPES = ["Photo", "Insight", "ExperienceIntro"]
OPTION_OR_CHOICE_PAGE_TYPES = [*OPTION_PAGE_TYPES, "ChooseOption"]
FLOW_LINK_TARGET_TYPES = [*OPTION_OR_CHOICE_PAGE_TYPES, "Ending"]
NEXT_OPTION_OR_END = [*FLOW_LINK_TARGET_TYPES, "FlowLink"]

ONBOARDING_FLOW = {
    "WelcomeLanguage": ["WelcomeIntro"],
    "WelcomeIntro": ["Welcome"],
    "Welcome": ["WelcomeCharacter"],
    "WelcomeCharacter": ["ChooseCharacter"],
    "ChooseCharacter": ["Introduction"],
    "Introduction": OPTION_OR_CHOICE_PAGE_TYPES,
}

EXPERIENCE_OPTION_FLOW = {
    "ExperienceIntro": ["ExperienceGallery"],
    "ExperienceGallery": ["Collage", "LogbookRecord", "ExperienceCreate"],
    "Collage": NEXT_OPTION_OR_END,
    "LogbookRecord": ["ExperienceCreate"],
    "ExperienceCreate": ["Timeline", *NEXT_OPTION_OR_END],
    "Timeline": NEXT_OPTION_OR_END,
}

PAGE_FLOW = {
    "Characters": [],
    **ONBOARDING_FLOW,
    "Photo": NEXT_OPTION_OR_END,
    "Insight": NEXT_OPTION_OR_END,
    "ChooseOption": OPTION_PAGE_TYPES,
    **EXPERIENCE_OPTION_FLOW,
    "FlowLink": [],
    "Ending": ["Survey"],
    "Survey": [],
}


def build_allowed_page_relations(page_flow, root_page_types):
    """Return ``(allowed_parents, allowed_subpages)`` derived from ``page_flow``."""
    allowed_subpages = {
        page_type: list(child_types) for page_type, child_types in page_flow.items()
    }
    allowed_parents = {page_type: [] for page_type in page_flow}
    for page_type, child_types in page_flow.items():
        for child_type in child_types:
            if child_type not in allowed_parents:
                raise ValueError(
                    f"{page_type!r} lists unknown child page type {child_type!r}"
                )
            allowed_parents[child_type].append(page_type)
    for page_type in root_page_types:
        allowed_parents[page_type] = ["wagtailcore.Page"]
    return allowed_parents, allowed_subpages


ALLOWED_PARENTS, ALLOWED_SUBPAGES = build_allowed_page_relations(
    PAGE_FLOW, ROOT_PAGE_TYPES
)
