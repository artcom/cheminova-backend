/*
 * Collapsing for the page explorer's tree listing.
 *
 * Rows arrive in depth-first order carrying their depth below the explored page, so a row's
 * descendants are simply the rows that follow it until the depth stops increasing. Which
 * branches are collapsed is kept per explored page in sessionStorage, so editing a page and
 * coming back does not throw the tree open again.
 */
(function () {
    'use strict';

    function setUpListing(listing) {
        var storageKey = 'page-explorer-collapsed:' + listing.dataset.treeListing;
        var rows = Array.prototype.slice.call(
            listing.querySelectorAll('tbody tr[data-tree-depth]'),
        );
        var collapsed = readCollapsed();

        function readCollapsed() {
            try {
                return new Set(JSON.parse(sessionStorage.getItem(storageKey)) || []);
            } catch (error) {
                return new Set();
            }
        }

        function rememberCollapsed() {
            try {
                sessionStorage.setItem(storageKey, JSON.stringify(Array.from(collapsed)));
            } catch (error) {
                /* Collapsing still works for this page view without storage. */
            }
        }

        function deselect(row) {
            var checkbox = row.querySelector('input[data-bulk-action-checkbox]');
            if (!checkbox || !checkbox.checked) return;
            // A hidden row must not stay selected, or a bulk action would reach pages the
            // editor can no longer see. The event lets Wagtail update its selection count.
            checkbox.checked = false;
            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
        }

        function applyCollapsedState() {
            var hiddenBelowDepth = null;
            rows.forEach(function (row) {
                var depth = Number(row.dataset.treeDepth);
                if (hiddenBelowDepth !== null && depth > hiddenBelowDepth) {
                    row.setAttribute('data-tree-hidden', '');
                    deselect(row);
                    return;
                }
                hiddenBelowDepth = null;
                row.removeAttribute('data-tree-hidden');

                var toggle = row.querySelector('[data-tree-toggle]');
                if (!toggle) return;
                var isCollapsed = collapsed.has(row.dataset.treePage);
                toggle.setAttribute('aria-expanded', String(!isCollapsed));
                if (isCollapsed) hiddenBelowDepth = depth;
            });
        }

        function setAll(shouldCollapse) {
            collapsed.clear();
            if (shouldCollapse) {
                rows.forEach(function (row) {
                    if (row.querySelector('[data-tree-toggle]')) {
                        collapsed.add(row.dataset.treePage);
                    }
                });
            }
            rememberCollapsed();
            applyCollapsedState();
        }

        // The expand/collapse all buttons sit in the header, outside the listing itself.
        document.addEventListener('click', function (event) {
            if (event.target.closest('[data-tree-expand-all]')) {
                setAll(false);
            } else if (event.target.closest('[data-tree-collapse-all]')) {
                setAll(true);
            }
        });

        listing.addEventListener('click', function (event) {
            var toggle = event.target.closest('[data-tree-toggle]');
            if (!toggle) return;
            var pageId = toggle.closest('tr[data-tree-depth]').dataset.treePage;
            if (collapsed.has(pageId)) {
                collapsed.delete(pageId);
            } else {
                collapsed.add(pageId);
            }
            rememberCollapsed();
            applyCollapsedState();
        });

        applyCollapsedState();
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-tree-listing]').forEach(setUpListing);
    });
})();
