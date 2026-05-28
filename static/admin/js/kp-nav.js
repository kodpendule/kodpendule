/**
 * Kod Pendule admin navigation helpers (Phase 2)
 */
(function () {
    "use strict";

    function openSidebarOnDesktop() {
        var main = document.getElementById("main");
        var navSidebar = document.getElementById("nav-sidebar");
        if (!main) {
            return;
        }
        var forceOpen = document.body.classList.contains("kp-admin-analytics");
        try {
            if (
                forceOpen ||
                (window.matchMedia("(min-width: 1024px)").matches &&
                    localStorage.getItem("django.admin.navSidebarIsOpen") !== "false")
            ) {
                main.classList.add("shifted");
                if (navSidebar) {
                    navSidebar.setAttribute("aria-expanded", "true");
                }
            }
        } catch (e) {
            if (forceOpen) {
                main.classList.add("shifted");
                if (navSidebar) {
                    navSidebar.setAttribute("aria-expanded", "true");
                }
            }
        }
    }

    function enhanceNavFilter() {
        var input = document.getElementById("nav-filter");
        var sidebar = document.getElementById("nav-sidebar");
        if (!input || !sidebar) {
            return;
        }

        input.addEventListener("input", function () {
            var query = input.value.trim().toLowerCase();
            var sections = sidebar.querySelectorAll(".kp-admin-nav__section");
            sections.forEach(function (section) {
                var visibleItems = 0;
                section.querySelectorAll(".kp-admin-nav__item").forEach(function (item) {
                    var label = item.textContent.toLowerCase();
                    var match = !query || label.indexOf(query) !== -1;
                    item.classList.toggle("is-hidden", !match);
                    if (match) {
                        visibleItems += 1;
                    }
                });
                section.classList.toggle("is-hidden", query.length > 0 && visibleItems === 0);
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        openSidebarOnDesktop();
        enhanceNavFilter();
    });
})();
