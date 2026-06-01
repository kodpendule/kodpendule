/**
 * Cookie consent banner — essential vs all (includes Google Maps).
 */
(function () {
    "use strict";

    var config = window.SHOP_COOKIE_CONSENT;
    if (!config || !config.cookieName) {
        return;
    }

    function setConsent(level) {
        var maxAge = config.maxAge || 31536000;
        var value = config.version + ":" + level;
        var secure = window.location.protocol === "https:" ? "; Secure" : "";
        document.cookie =
            config.cookieName +
            "=" +
            encodeURIComponent(value) +
            "; path=/; max-age=" +
            maxAge +
            "; SameSite=Lax" +
            secure;
        window.location.reload();
    }

    function clearConsent() {
        document.cookie = config.cookieName + "=; path=/; max-age=0";
    }

    function showBanner() {
        var banner = document.getElementById("shop-cookie-banner");
        if (!banner) {
            return;
        }
        banner.hidden = false;
        document.body.classList.add("shop-has-cookie-banner");
    }

    document.addEventListener("DOMContentLoaded", function () {
        var banner = document.getElementById("shop-cookie-banner");
        if (banner) {
            showBanner();
        }

        document.querySelectorAll(".js-cookie-consent-all").forEach(function (btn) {
            btn.addEventListener("click", function () {
                setConsent("all");
            });
        });

        document.querySelectorAll(".js-cookie-consent-essential").forEach(function (btn) {
            btn.addEventListener("click", function () {
                setConsent("essential");
            });
        });

        document.querySelectorAll(".js-cookie-settings").forEach(function (btn) {
            btn.addEventListener("click", function () {
                clearConsent();
                showBanner();
            });
        });
    });
})();
