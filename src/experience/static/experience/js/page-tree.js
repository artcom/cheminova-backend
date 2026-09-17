/*
 * Collapsing for the page explorer's tree listing.
 *
 * Rows arrive in depth-first order carrying their depth below the explored page, so a row's
 * descendants are simply the rows that follow it until the depth stops increasing. Which
 * branches are collapsed is kept per explored page in sessionStorage, so editing a page and
 * coming back does not throw the tree open again.
 *
 * The toolbar and the table both live inside #listing-results, the region Wagtail's w-swap
 * controller replaces wholesale when the admin search box is used, so nothing here may hold
 * a reference to a specific DOM node across an interaction: every handler re-reads the current
 * listing from the document, and re-runs after w-swap reports a swap ("w-swap:success").
 */
(function () {
    'use strict';

    function currentListing() {
        return document.querySelector('[data-tree-listing]');
    }

    function storageKey(listing) {
        return 'page-explorer-collapsed:' + listing.dataset.treeListing;
    }

    function readCollapsed(listing) {
        try {
            return new Set(JSON.parse(sessionStorage.getItem(storageKey(listing))) || []);
        } catch (error) {
            return new Set();
        }
    }

    function writeCollapsed(listing, collapsed) {
        try {
            sessionStorage.setItem(storageKey(listing), JSON.stringify(Array.from(collapsed)));
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

    function applyCollapsedState(listing) {
        var collapsed = readCollapsed(listing);
        var rows = Array.prototype.slice.call(
            listing.querySelectorAll('tbody tr[data-tree-depth]'),
        );
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

    function setAll(listing, shouldCollapse) {
        var collapsed = new Set();
        if (shouldCollapse) {
            listing.querySelectorAll('tbody tr[data-tree-depth]').forEach(function (row) {
                if (row.querySelector('[data-tree-toggle]')) collapsed.add(row.dataset.treePage);
            });
        }
        writeCollapsed(listing, collapsed);
        applyCollapsedState(listing);
    }

    document.addEventListener('click', function (event) {
        var toggle = event.target.closest('[data-tree-toggle]');
        if (toggle) {
            var listing = toggle.closest('[data-tree-listing]');
            var pageId = toggle.closest('tr[data-tree-depth]').dataset.treePage;
            var collapsed = readCollapsed(listing);
            if (collapsed.has(pageId)) {
                collapsed.delete(pageId);
            } else {
                collapsed.add(pageId);
            }
            writeCollapsed(listing, collapsed);
            applyCollapsedState(listing);
            return;
        }

        // The toolbar sits above the table, outside [data-tree-listing] itself, so its
        // buttons fall back to the (only) listing the current page can have.
        var expandAll = event.target.closest('[data-tree-expand-all]');
        var collapseAll = event.target.closest('[data-tree-collapse-all]');
        if (expandAll || collapseAll) {
            var target = currentListing();
            if (target) setAll(target, Boolean(collapseAll));
        }
    });

    function applyToCurrentListing() {
        var listing = currentListing();
        if (listing) applyCollapsedState(listing);
    }

    document.addEventListener('DOMContentLoaded', applyToCurrentListing);
    document.addEventListener('w-swap:success', applyToCurrentListing);
})();
