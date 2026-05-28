/**
 * Kod Pendule — header UX (close mobile menu on navigate)
 */
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        var panel = document.getElementById("shopMobileNav");
        if (!panel || typeof bootstrap === "undefined") {
            return;
        }

        panel.querySelectorAll("a.nav-link, a.shop-btn, button.shop-btn").forEach(function (el) {
            el.addEventListener("click", function () {
                var instance = bootstrap.Offcanvas.getInstance(panel);
                if (instance) {
                    instance.hide();
                }
            });
        });

        /* Don't close when submitting language buttons inside offcanvas */
        panel.querySelectorAll(".shop-lang__btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var instance = bootstrap.Offcanvas.getInstance(panel);
                if (instance) {
                    instance.hide();
                }
            });
        });
    });
})();
