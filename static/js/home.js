/**
 * Kod Pendule — homepage scroll reveals & light motion
 */
(function () {
    "use strict";

    function prefersReducedMotion() {
        return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    function initReveals() {
        var root = document.querySelector(".shop-home");
        if (!root) {
            return;
        }

        var revealEls = root.querySelectorAll("[data-reveal], [data-reveal-stagger]");
        if (!revealEls.length) {
            return;
        }

        if (prefersReducedMotion()) {
            revealEls.forEach(function (el) {
                el.classList.add("is-revealed");
            });
            return;
        }

        if (!("IntersectionObserver" in window)) {
            revealEls.forEach(function (el) {
                el.classList.add("is-revealed");
            });
            return;
        }

        var observer = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    entry.target.classList.add("is-revealed");
                    observer.unobserve(entry.target);
                });
            },
            {
                threshold: 0.12,
                rootMargin: "0px 0px -48px 0px",
            }
        );

        revealEls.forEach(function (el) {
            observer.observe(el);
        });
    }

    function initStatCounters() {
        if (prefersReducedMotion()) {
            return;
        }

        var stats = document.querySelectorAll(".shop-hero__stat-value[data-count-to]");
        if (!stats.length || !("IntersectionObserver" in window)) {
            return;
        }

        function animateValue(el) {
            var target = parseInt(el.getAttribute("data-count-to"), 10);
            if (Number.isNaN(target) || target <= 0) {
                return;
            }
            var duration = 900;
            var start = performance.now();

            function frame(now) {
                var progress = Math.min((now - start) / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = String(Math.round(target * eased));
                if (progress < 1) {
                    requestAnimationFrame(frame);
                }
            }

            requestAnimationFrame(frame);
        }

        var counterObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) {
                        return;
                    }
                    animateValue(entry.target);
                    counterObserver.unobserve(entry.target);
                });
            },
            { threshold: 0.5 }
        );

        stats.forEach(function (el) {
            counterObserver.observe(el);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initReveals();
        initStatCounters();
    });
})();
