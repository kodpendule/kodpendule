(function () {
  "use strict";

  const citySelect = document.getElementById("id_shipping_city");
  const deliveryEl = document.getElementById("city-delivery-data");
  const todayEl = document.getElementById("checkout-today-data");
  const shippingDisplays = document.querySelectorAll(".js-shipping-price");
  const totalDisplay = document.getElementById("checkout-total-display");
  const summaryCard = document.querySelector("[data-checkout-subtotal]");
  const shippingHint = document.getElementById("checkout-shipping-hint");
  const dateRow = document.getElementById("shop-delivery-date-row");
  const dateInput = document.getElementById("id_requested_delivery_date");
  const timingInputs = document.querySelectorAll('input[name="delivery_timing"]');

  if (!deliveryEl || !citySelect) {
    return;
  }

  const cityDelivery = JSON.parse(deliveryEl.textContent);
  const checkoutToday = todayEl ? JSON.parse(todayEl.textContent) : null;
  const subtotal = summaryCard
    ? parseFloat(summaryCard.getAttribute("data-checkout-subtotal") || "0")
    : 0;
  const currency = summaryCard
    ? summaryCard.getAttribute("data-currency") || ""
    : "";

  function formatPrice(value) {
    if (value === null || value === undefined || value === "") return "—";
    const num = parseFloat(value);
    if (Number.isNaN(num)) return "—";
    return num.toLocaleString("sr-RS", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function selectedTiming() {
    const checked = document.querySelector('input[name="delivery_timing"]:checked');
    return checked ? checked.value : "same_day";
  }

  function isScheduledFree() {
    if (selectedTiming() !== "scheduled") {
      return false;
    }
    if (!dateInput || !dateInput.value || !checkoutToday) {
      return false;
    }
    return dateInput.value > checkoutToday;
  }

  function cityRules(cityId) {
    return cityDelivery[cityId] || {};
  }

  function sameDayShipping(cityId) {
    const rules = cityRules(cityId);
    const cityBase = rules.base ? parseFloat(rules.base) : NaN;
    const threshold = rules.threshold ? parseFloat(rules.threshold) : NaN;
    const discountedPrice = rules.discounted_shipping_price
      ? parseFloat(rules.discounted_shipping_price)
      : NaN;
    const thresholdMode = rules.threshold_shipping_mode || "free";

    if (
      !Number.isNaN(threshold) &&
      threshold > 0 &&
      !Number.isNaN(subtotal) &&
      subtotal >= threshold
    ) {
      if (thresholdMode === "discounted" && !Number.isNaN(discountedPrice)) {
        return discountedPrice;
      }
      return 0;
    }
    return cityBase;
  }

  function effectiveShipping(cityId) {
    if (isScheduledFree()) {
      return 0;
    }
    return sameDayShipping(cityId);
  }

  function updateDeliveryDateVisibility() {
    if (!dateRow) {
      return;
    }
    dateRow.hidden = selectedTiming() !== "scheduled";
  }

  function updateShippingHint(cityId, appliedFree, appliedDiscount) {
    if (!shippingHint) {
      return;
    }
    if (isScheduledFree()) {
      shippingHint.textContent =
        shippingHint.getAttribute("data-msg-scheduled-free") || "";
      shippingHint.hidden = !shippingHint.textContent;
      return;
    }

    const rules = cityRules(cityId);
    const threshold = rules.threshold ? parseFloat(rules.threshold) : NaN;
    if (Number.isNaN(threshold) || threshold <= 0) {
      shippingHint.hidden = true;
      return;
    }
    if (subtotal >= threshold) {
      if (appliedFree) {
        shippingHint.textContent =
          shippingHint.getAttribute("data-msg-free") || "";
        shippingHint.hidden = !shippingHint.textContent;
      } else if (appliedDiscount) {
        shippingHint.textContent =
          shippingHint.getAttribute("data-msg-discounted") || "";
        shippingHint.hidden = !shippingHint.textContent;
      } else {
        shippingHint.hidden = true;
      }
    } else {
      const remaining = threshold - subtotal;
      const template = shippingHint.getAttribute("data-msg-remaining") || "";
      shippingHint.textContent = template.replace("__AMOUNT__", formatPrice(remaining));
      shippingHint.hidden = !shippingHint.textContent;
    }
  }

  function updateShippingPrice() {
    const id = citySelect.value;
    const rules = cityRules(id);
    const threshold = rules.threshold ? parseFloat(rules.threshold) : NaN;
    const discountedPrice = rules.discounted_shipping_price
      ? parseFloat(rules.discounted_shipping_price)
      : NaN;
    const thresholdMode = rules.threshold_shipping_mode || "free";
    const shipping = effectiveShipping(id);
    const shippingText = formatPrice(shipping);
    const appliedFree =
      !isScheduledFree() &&
      !Number.isNaN(threshold) &&
      threshold > 0 &&
      subtotal >= threshold &&
      thresholdMode === "free";
    const appliedDiscount =
      !isScheduledFree() &&
      !Number.isNaN(threshold) &&
      threshold > 0 &&
      subtotal >= threshold &&
      thresholdMode === "discounted" &&
      !Number.isNaN(discountedPrice);

    shippingDisplays.forEach(function (el) {
      el.textContent = shippingText;
    });
    if (totalDisplay && !Number.isNaN(subtotal)) {
      const amount = Number.isNaN(shipping) ? subtotal : subtotal + shipping;
      const formatted = formatPrice(amount);
      totalDisplay.textContent = currency ? formatted + " " + currency : formatted;
    }
    updateShippingHint(id, appliedFree, appliedDiscount);
  }

  citySelect.addEventListener("change", updateShippingPrice);
  timingInputs.forEach(function (input) {
    input.addEventListener("change", function () {
      updateDeliveryDateVisibility();
      updateShippingPrice();
    });
  });
  if (dateInput) {
    dateInput.addEventListener("change", updateShippingPrice);
    dateInput.addEventListener("input", updateShippingPrice);
  }

  updateDeliveryDateVisibility();
  updateShippingPrice();
})();
