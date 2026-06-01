(function () {
  "use strict";

  function initBackToTop() {
    var button = document.getElementById("shop-back-to-top");
    if (!button) {
      return;
    }

    var revealOffset = 320;

    function toggleVisibility() {
      var show = window.scrollY > revealOffset;
      button.hidden = !show;
    }

    button.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", toggleVisibility, { passive: true });
    toggleVisibility();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBackToTop);
  } else {
    initBackToTop();
  }
})();
