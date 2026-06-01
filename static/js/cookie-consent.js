/**
 * Cookie consent banner — acknowledges essential shop cookies.
 */
(function () {
    "use strict";

    var config = window.SHOP_COOKIE_CONSENT;
    if (!config || !config.cookieName) {
        return;
    }

    function escapeRegExp(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function hasConsent() {
        var match = document.cookie.match(
            new RegExp("(?:^|; )" + escapeRegExp(config.cookieName) + "=([^;]*)")
        );
        if (!match) {
            return false;
        }
        var raw = decodeURIComponent(match[1].replace(/\+/g, " "));
        var parts = raw.split(":", 2);
        return parts.length === 2 && parts[0] === config.version;
    }

    function writeConsent(level) {
        var maxAge = config.maxAge || 31536000;
        var value = config.version + ":" + level;
        var secure = window.location.protocol === "https:" ? "; Secure" : "";
        document.cookie =
            config.cookieName +
            "=" +
            value +
            "; path=/; max-age=" +
            maxAge +
            "; SameSite=Lax" +
            secure;
    }

    function clearConsent() {
        var secure = window.location.protocol === "https:" ? "; Secure" : "";
        document.cookie =
            config.cookieName + "=; path=/; max-age=0; SameSite=Lax" + secure;
    }

    function hideBanner() {
        var banner = document.getElementById("shop-cookie-banner");
        if (banner) {
            banner.hidden = true;
        }
        document.body.classList.remove("shop-has-cookie-banner");
    }

    function showBanner() {
        var banner = document.getElementById("shop-cookie-banner");
        if (!banner) {
            return;
        }
        banner.hidden = false;
        document.body.classList.add("shop-has-cookie-banner");
    }

    function acceptCookies() {
        writeConsent("all");
        hideBanner();
    }

    function declineCookies() {
        writeConsent("essential");
        hideBanner();
    }

    function openCookieSettings() {
        clearConsent();
        showBanner();
    }

    document.addEventListener("click", function (event) {
        if (event.target.closest(".js-cookie-consent-accept")) {
            event.preventDefault();
            acceptCookies();
            return;
        }
        if (event.target.closest(".js-cookie-consent-decline")) {
            event.preventDefault();
            declineCookies();
            return;
        }
        if (event.target.closest(".js-cookie-settings")) {
            event.preventDefault();
            openCookieSettings();
        }
    });

    document.addEventListener("DOMContentLoaded", function () {
        if (hasConsent()) {
            hideBanner();
        } else {
            showBanner();
        }
    });
})();
