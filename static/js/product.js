/**
 * Kod Pendule — product detail UX (quantity stepper)
 * Lightweight: no dependencies, no animation.
 */
(function () {
    "use strict";

    function clamp(n, min, max) {
        if (Number.isNaN(n)) return min;
        return Math.min(max, Math.max(min, n));
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-shop-qty]").forEach(function (wrap) {
            var input = wrap.querySelector("input[type='number']");
            var inc = wrap.querySelector("[data-shop-qty-inc]");
            var dec = wrap.querySelector("[data-shop-qty-dec]");
            if (!input || !inc || !dec) return;

            var min = parseInt(input.getAttribute("min") || "1", 10);
            var max = parseInt(input.getAttribute("max") || "9999", 10);

            function setValue(next) {
                var v = clamp(next, min, max);
                input.value = String(v);
                input.dispatchEvent(new Event("change", { bubbles: true }));
            }

            inc.addEventListener("click", function () {
                setValue(parseInt(input.value || String(min), 10) + 1);
            });
            dec.addEventListener("click", function () {
                setValue(parseInt(input.value || String(min), 10) - 1);
            });

            input.addEventListener("input", function () {
                var v = parseInt(input.value || String(min), 10);
                if (Number.isNaN(v)) return;
                setValue(v);
            });
        });
    });
})();

