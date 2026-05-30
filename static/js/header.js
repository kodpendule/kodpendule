/**
 * Kod Pendule — header UX (scroll menu + close panel on navigate)
 */
(function () {
    "use strict";

    var SCROLL_THRESHOLD = 96;
    var FAB_HIDE_MS = 420;
    var MOBILE_MQ = window.matchMedia("(max-width: 991.98px)");

    function closePanel(panel) {
        if (!panel || typeof bootstrap === "undefined") {
            return;
        }
        var instance = bootstrap.Offcanvas.getInstance(panel);
        if (instance) {
            instance.hide();
        }
    }

    function bindPanelClose(panel) {
        if (!panel) {
            return;
        }

        panel.querySelectorAll("a.nav-link, a.shop-btn, button.shop-btn, a.shop-header-panel__cart").forEach(function (el) {
            el.addEventListener("click", function () {
                closePanel(panel);
            });
        });

        panel.querySelectorAll(".shop-lang__btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                closePanel(panel);
            });
        });
    }

    function syncHeaderPanelMode(panel, fab) {
        if (!panel || !fab) {
            return;
        }

        var mobile = MOBILE_MQ.matches;
        var open = panel.classList.contains("show");

        if (open) {
            closePanel(panel);
        }

        panel.classList.remove("offcanvas-start", "offcanvas-bottom");
        fab.classList.remove("shop-header-fab--desktop", "shop-header-fab--mobile");

        if (mobile) {
            panel.classList.add("offcanvas-bottom");
            fab.classList.add("shop-header-fab--mobile");
        } else {
            panel.classList.add("offcanvas-start");
            fab.classList.add("shop-header-fab--desktop");
        }
    }

    function initScrollFab(fab) {
        if (!fab) {
            return;
        }

        var ticking = false;
        var hideTimer = null;

        function showFab() {
            window.clearTimeout(hideTimer);
            fab.hidden = false;
            fab.setAttribute("aria-hidden", "false");
            window.requestAnimationFrame(function () {
                fab.classList.add("is-visible");
            });
        }

        function hideFab() {
            fab.classList.remove("is-visible");
            fab.setAttribute("aria-hidden", "true");
            window.clearTimeout(hideTimer);
            hideTimer = window.setTimeout(function () {
                if (!fab.classList.contains("is-visible")) {
                    fab.hidden = true;
                }
            }, FAB_HIDE_MS);
        }

        function updateFab() {
            if (window.scrollY > SCROLL_THRESHOLD) {
                if (!fab.classList.contains("is-visible")) {
                    showFab();
                }
            } else if (fab.classList.contains("is-visible") || !fab.hidden) {
                hideFab();
            } else {
                fab.hidden = true;
                fab.setAttribute("aria-hidden", "true");
            }
            ticking = false;
        }

        function onScroll() {
            if (!ticking) {
                window.requestAnimationFrame(updateFab);
                ticking = true;
            }
        }

        window.addEventListener("scroll", onScroll, { passive: true });
        updateFab();
    }

    document.addEventListener("DOMContentLoaded", function () {
        var panel = document.getElementById("shopHeaderPanel");
        var fab = document.getElementById("shopHeaderFab");

        syncHeaderPanelMode(panel, fab);
        bindPanelClose(panel);
        initScrollFab(fab);

        if (typeof MOBILE_MQ.addEventListener === "function") {
            MOBILE_MQ.addEventListener("change", function () {
                syncHeaderPanelMode(panel, fab);
            });
        } else if (typeof MOBILE_MQ.addListener === "function") {
            MOBILE_MQ.addListener(function () {
                syncHeaderPanelMode(panel, fab);
            });
        }
    });
})();
