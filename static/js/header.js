/**
 * Kod Pendule — header UX (scroll menu + close panel on navigate)
 */
(function () {
    "use strict";

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

    document.addEventListener("DOMContentLoaded", function () {
        var panel = document.getElementById("shopHeaderPanel");
        var fab = document.getElementById("shopHeaderFab");

        syncHeaderPanelMode(panel, fab);
        bindPanelClose(panel);
        if (typeof window.shopInitScrollFloatControls === "function") {
            window.shopInitScrollFloatControls([
                { el: fab, manageAria: true },
                { el: document.getElementById("shop-back-to-top"), manageAria: false },
            ]);
        }

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
