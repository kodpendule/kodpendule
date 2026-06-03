/**
 * Shared scroll reveal for floating actions (menu FAB, back to top).
 */
(function () {
    "use strict";

    var SCROLL_THRESHOLD = 96;
    var HIDE_MS = 420;

    function initScrollFloatControls(controls) {
        controls = controls.filter(function (item) {
            return item && item.el;
        });
        if (!controls.length) {
            return;
        }

        var ticking = false;
        var hideTimer = null;

        function isAnyVisible() {
            return controls.some(function (item) {
                return (
                    item.el.classList.contains("is-visible") || !item.el.hidden
                );
            });
        }

        function isAllVisible() {
            return controls.every(function (item) {
                return item.el.classList.contains("is-visible");
            });
        }

        function showAll() {
            window.clearTimeout(hideTimer);
            controls.forEach(function (item) {
                item.el.hidden = false;
                if (item.manageAria) {
                    item.el.setAttribute("aria-hidden", "false");
                }
            });
            window.requestAnimationFrame(function () {
                window.requestAnimationFrame(function () {
                    controls.forEach(function (item) {
                        item.el.classList.add("is-visible");
                    });
                });
            });
        }

        function hideAll() {
            controls.forEach(function (item) {
                item.el.classList.remove("is-visible");
                if (item.manageAria) {
                    item.el.setAttribute("aria-hidden", "true");
                }
            });
            window.clearTimeout(hideTimer);
            hideTimer = window.setTimeout(function () {
                controls.forEach(function (item) {
                    if (!item.el.classList.contains("is-visible")) {
                        item.el.hidden = true;
                    }
                });
            }, HIDE_MS);
        }

        function hideAllImmediate() {
            controls.forEach(function (item) {
                item.el.hidden = true;
                item.el.classList.remove("is-visible");
                if (item.manageAria) {
                    item.el.setAttribute("aria-hidden", "true");
                }
            });
        }

        function updateControls() {
            if (window.scrollY > SCROLL_THRESHOLD) {
                if (!isAllVisible()) {
                    showAll();
                }
            } else if (isAnyVisible()) {
                hideAll();
            } else {
                hideAllImmediate();
            }
            ticking = false;
        }

        function onScroll() {
            if (!ticking) {
                window.requestAnimationFrame(updateControls);
                ticking = true;
            }
        }

        window.addEventListener("scroll", onScroll, { passive: true });
        updateControls();
    }

    window.shopInitScrollFloatControls = initScrollFloatControls;
})();
