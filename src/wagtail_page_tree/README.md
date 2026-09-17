# wagtail_page_tree

Replaces Wagtail's page explorer listing with an indented tree: instead of the direct children
of the page being explored, the listing shows its descendants down to a configurable depth, in
depth-first order, with collapsible branches.

Editors get a toolbar above the listing with a "Tree view" depth picker and expand-all /
collapse-all buttons. The chosen depth is remembered per session, the collapsed branches per
explored page (in the browser's `sessionStorage`).

Tree mode steps aside whenever the listing means something other than "this subtree": while
searching, while filtering, and when a column sort is explicitly asked for. In those cases the
stock flat listing is shown, and only the depth picker stays on screen so there is a way back.

## Install

The app is self-contained: no models, no migrations, no URLs, no template overrides in your
project. Copy the `wagtail_page_tree` directory onto your Python path and add it to
`INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "wagtail_page_tree",
    ...
]
```

Its `AppConfig.ready()` points `wagtail.admin.viewsets.pages.base_page_viewset` at its own
index view. That is deliberate rather than a registered `PageViewSet`: the "Pages" sidebar item
resolves to `wagtailadmin_explore_root`, which is wired straight to `base_page_viewset` and
never consults the viewset registry. It follows that the app **conflicts with anything else
that replaces `base_page_viewset.index_view_class`** — the last `ready()` to run wins, so list
this app before any of your own that means to build on it.

## Settings

| Setting | Default | Meaning |
| --- | --- | --- |
| `PAGE_EXPLORER_TREE_DEPTH` | `1` | Levels of descendants listed under the explored page. `1` is Wagtail's stock listing of direct children only, i.e. the feature off. |
| `PAGE_EXPLORER_TREE_DEPTH_CHOICES` | `[1]` | The levels the "Tree view" dropdown offers. Include `1` so editors can switch tree mode off. |

Both are optional — unset, the app installs itself and changes nothing visible. A typical
configuration:

```python
PAGE_EXPLORER_TREE_DEPTH = 3
PAGE_EXPLORER_TREE_DEPTH_CHOICES = [1, 2, 3, 5, 10]
```

Permissions are unaffected: the listing is filtered through Wagtail's own
`page_permission_policy.explorable_instances()`, so a deeper tree never reveals a page the
stock listing would have hidden.

## Assets

`static/wagtail_page_tree/css/page-tree.css` and `.../js/page-tree.js` are linked from
`templates/wagtail_page_tree/explorer/tree_index.html` with the plain `{% static %}` tag, each
inside a `{% block tree_css %}` / `{% block tree_js %}` of its own. To serve them differently —
hashed URLs, a bundled build — extend that template, override the block, and point
`TreeExplorableIndexView.template_name` at your version rather than forking the file.

The CSS styles Wagtail's own admin classes and custom properties; there is no build step.

Under `ManifestStaticFilesStorage`, `{% static %}` raises rather than guessing when an asset is
missing from the manifest, and tests run with `DEBUG = False` — so run `collectstatic` after
adding the app, before running the suite. That strictness is deliberate: it is what turns a
renamed or unshipped asset into a failing test instead of a silent 404.

## Wagtail compatibility

Developed against **Wagtail 7.4**. The app builds on admin internals and template names that
Wagtail does not treat as public API:

- `wagtail.admin.views.pages.listing.ExplorableIndexView`
- `wagtail.admin.ui.tables.pages.PageTable`, `PageTitleColumn`
- `wagtail.admin.widgets.button.BaseButton`, `Button`, `ButtonWithDropdown`
- `wagtail.admin.viewsets.pages.base_page_viewset`
- the templates `wagtailadmin/pages/explorable_index.html`,
  `explorable_index_results.html`, `listing/_page_title_explore.html` and
  `bulk_actions/footer.html`

`tests.py` exercises every one of them, including the `footer.html` gating that lets the app
drop "Select all pages in listing" (which resolves server-side to direct children, so in tree
mode it would act on a different set than the one on screen). Run the suite after any Wagtail
upgrade; it is the drift detector.

## Turning it into a package

The directory is laid out so it can be lifted out as an installable distribution unchanged: add
a `pyproject.toml` with a build backend configured to ship the `templates/` and `static/` trees
as package data. Nothing in the app refers to anything outside itself.
