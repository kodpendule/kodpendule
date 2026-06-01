(function () {
  "use strict";

  const citySelect = document.getElementById("id_shipping_city");
  const pricesEl = document.getElementById("city-prices-data");
  const rulesEl = document.getElementById("checkout-shipping-rules");
  const shippingDisplays = document.querySelectorAll(".js-shipping-price");
  const totalDisplay = document.getElementById("checkout-total-display");
  const summaryCard = document.querySelector("[data-checkout-subtotal]");
  const shippingHint = document.getElementById("checkout-shipping-hint");

  if (!pricesEl || !citySelect) {
    return;
  }

  const prices = JSON.parse(pricesEl.textContent);
  const rules = rulesEl ? JSON.parse(rulesEl.textContent) : {};
  const subtotal = summaryCard
    ? parseFloat(summaryCard.getAttribute("data-checkout-subtotal") || "0")
    : 0;
  const currency = summaryCard
    ? summaryCard.getAttribute("data-currency") || ""
    : "";

  const threshold = rules.free_shipping_threshold
    ? parseFloat(rules.free_shipping_threshold)
    : NaN;
  const discountedPrice = rules.discounted_shipping_price
    ? parseFloat(rules.discounted_shipping_price)
    : NaN;
  const thresholdMode = rules.threshold_shipping_mode || "free";

  function formatPrice(value) {
    if (value === null || value === undefined || value === "") return "—";
    const num = parseFloat(value);
    if (Number.isNaN(num)) return "—";
    return num.toLocaleString("sr-RS", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function effectiveShipping(cityBasePrice) {
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
    return cityBasePrice;
  }

  function updateShippingHint(appliedFree, appliedDiscount) {
    if (!shippingHint || Number.isNaN(threshold) || threshold <= 0) {
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
    const cityBase = prices[id] ? parseFloat(prices[id]) : NaN;
    const shipping = effectiveShipping(cityBase);
    const shippingText = formatPrice(shipping);
    const appliedFree =
      !Number.isNaN(threshold) &&
      threshold > 0 &&
      subtotal >= threshold &&
      thresholdMode === "free";
    const appliedDiscount =
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
    updateShippingHint(appliedFree, appliedDiscount);
  }

  citySelect.addEventListener("change", updateShippingPrice);
  updateShippingPrice();
})();
