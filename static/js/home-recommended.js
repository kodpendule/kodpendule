/**
 * Homepage — recommended products carousel (5 per page, arrows + swipe).
 */
(function () {
    "use strict";

    function initRecommendedCarousel() {
        var root = document.querySelector("[data-recommended-carousel]");
        if (!root) {
            return;
        }

        var track = root.querySelector("[data-recommended-track]");
        var viewport = root.querySelector("[data-recommended-viewport]");
        var pages = root.querySelectorAll("[data-recommended-page]");
        var prevBtn = root.querySelector("[data-recommended-prev]");
        var nextBtn = root.querySelector("[data-recommended-next]");
        var dots = root.querySelectorAll("[data-recommended-dot]");
        var status = root.querySelector("[data-recommended-status]");

        if (!track || !pages.length) {
            return;
        }

        var pageCount = pages.length;
        var current = 0;
        var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        function pageLabel(index) {
            return String(index + 1) + " / " + String(pageCount);
        }

        function updateUi() {
            var offset = current * -100;
            track.style.transform = "translate3d(" + offset + "%, 0, 0)";

            pages.forEach(function (page, index) {
                page.setAttribute("aria-hidden", index === current ? "false" : "true");
            });

            if (prevBtn) {
                prevBtn.disabled = current === 0;
            }
            if (nextBtn) {
                nextBtn.disabled = current === pageCount - 1;
            }

            dots.forEach(function (dot, index) {
                var active = index === current;
                dot.classList.toggle("is-active", active);
                dot.setAttribute("aria-selected", active ? "true" : "false");
            });

            if (status) {
                var template = status.getAttribute("data-page-template");
                if (template) {
                    status.textContent = template
                        .replace("__NUM__", String(current + 1))
                        .replace("__TOTAL__", String(pageCount));
                } else {
                    status.textContent = pageLabel(current);
                }
            }
        }

        function goTo(index) {
            var next = Math.max(0, Math.min(pageCount - 1, index));
            if (next === current) {
                return;
            }
            current = next;
            updateUi();
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", function () {
                goTo(current - 1);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", function () {
                goTo(current + 1);
            });
        }

        dots.forEach(function (dot) {
            dot.addEventListener("click", function () {
                var target = parseInt(dot.getAttribute("data-recommended-dot"), 10);
                if (!Number.isNaN(target)) {
                    goTo(target);
                }
            });
        });

        var touchStartX = 0;
        var touchDeltaX = 0;
        var swiping = false;

        if (viewport && !reducedMotion) {
            viewport.addEventListener(
                "touchstart",
                function (event) {
                    if (!event.touches.length) {
                        return;
                    }
                    touchStartX = event.touches[0].clientX;
                    touchDeltaX = 0;
                    swiping = true;
                },
                { passive: true }
            );

            viewport.addEventListener(
                "touchmove",
                function (event) {
                    if (!swiping || !event.touches.length) {
                        return;
                    }
                    touchDeltaX = event.touches[0].clientX - touchStartX;
                },
                { passive: true }
            );

            viewport.addEventListener(
                "touchend",
                function () {
                    if (!swiping) {
                        return;
                    }
                    swiping = false;
                    if (Math.abs(touchDeltaX) < 48) {
                        return;
                    }
                    if (touchDeltaX < 0) {
                        goTo(current + 1);
                    } else {
                        goTo(current - 1);
                    }
                },
                { passive: true }
            );
        }

        root.addEventListener("keydown", function (event) {
            if (event.key === "ArrowLeft") {
                goTo(current - 1);
            } else if (event.key === "ArrowRight") {
                goTo(current + 1);
            }
        });

        updateUi();
    }

    document.addEventListener("DOMContentLoaded", initRecommendedCarousel);
})();
