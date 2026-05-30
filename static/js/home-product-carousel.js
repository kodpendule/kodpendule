/**
 * Homepage product carousels — arrows, touch swipe, scroll-snap.
 */
(function () {
    "use strict";

    function initProductCarousel(root) {
        var viewport = root.querySelector("[data-carousel-viewport]");
        var track = root.querySelector("[data-carousel-track]");
        var prevBtn = root.querySelector("[data-carousel-prev]");
        var nextBtn = root.querySelector("[data-carousel-next]");
        var slides = root.querySelectorAll("[data-carousel-slide]");

        if (!viewport || !track || !slides.length) {
            return;
        }

        function scrollStep() {
            var slide = slides[0];
            if (!slide) {
                return viewport.clientWidth;
            }
            var styles = window.getComputedStyle(track);
            var gap = parseFloat(styles.columnGap || styles.gap || "0") || 0;
            return slide.getBoundingClientRect().width + gap;
        }

        function updateControls() {
            var maxScroll = viewport.scrollWidth - viewport.clientWidth;
            var atStart = viewport.scrollLeft <= 1;
            var atEnd = viewport.scrollLeft >= maxScroll - 1;

            if (prevBtn) {
                prevBtn.disabled = atStart || maxScroll <= 0;
            }
            if (nextBtn) {
                nextBtn.disabled = atEnd || maxScroll <= 0;
            }

            var hideArrows = maxScroll <= 0;
            root.classList.toggle("is-scrollable", !hideArrows);
        }

        function scrollByStep(direction) {
            viewport.scrollBy({
                left: direction * scrollStep(),
                behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
                    ? "auto"
                    : "smooth",
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", function () {
                scrollByStep(-1);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", function () {
                scrollByStep(1);
            });
        }

        viewport.addEventListener("scroll", updateControls, { passive: true });

        viewport.addEventListener("keydown", function (event) {
            if (event.key === "ArrowLeft") {
                event.preventDefault();
                scrollByStep(-1);
            } else if (event.key === "ArrowRight") {
                event.preventDefault();
                scrollByStep(1);
            }
        });

        var resizeTimer;
        window.addEventListener("resize", function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(updateControls, 120);
        });

        updateControls();
    }

    function initAll() {
        document.querySelectorAll("[data-product-carousel]").forEach(initProductCarousel);
    }

    document.addEventListener("DOMContentLoaded", initAll);
})();
