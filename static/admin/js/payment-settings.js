(function () {
  "use strict";

  function toggleDiscountedRow() {
    var modeSelect = document.querySelector(".kp-promo-mode-select");
    var discountedRow = document.getElementById("kp-promo-discounted-row");
    if (!modeSelect || !discountedRow) {
      return;
    }
    var show = modeSelect.value === "discounted";
    discountedRow.hidden = !show;
  }

  function initCitySelector() {
    var citySelect = document.getElementById("kp-payment-city");
    var cityForm = document.getElementById("kp-payment-city-form");
    if (!citySelect || !cityForm) {
      return;
    }
    citySelect.addEventListener("change", function () {
      var url = new URL(window.location.href);
      url.searchParams.set("city", citySelect.value);
      window.location.href = url.toString();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      toggleDiscountedRow();
      initCitySelector();
      var modeSelect = document.querySelector(".kp-promo-mode-select");
      if (modeSelect) {
        modeSelect.addEventListener("change", toggleDiscountedRow);
      }
    });
  } else {
    toggleDiscountedRow();
    initCitySelector();
    var modeSelect = document.querySelector(".kp-promo-mode-select");
    if (modeSelect) {
      modeSelect.addEventListener("change", toggleDiscountedRow);
    }
  }
})();
