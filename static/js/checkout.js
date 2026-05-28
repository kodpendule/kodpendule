(function () {
  "use strict";

  const citySelect = document.getElementById("id_shipping_city");
  const billingSame = document.getElementById("id_billing_same");
  const billingFields = document.getElementById("billing-fields");
  const pricesEl = document.getElementById("city-prices-data");
  const shippingDisplays = document.querySelectorAll(".js-shipping-price");
  const totalDisplay = document.getElementById("checkout-total-display");
  const summaryCard = document.querySelector("[data-checkout-subtotal]");

  if (!pricesEl || !citySelect) {
    return;
  }

  const prices = JSON.parse(pricesEl.textContent);
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

  function updateShippingPrice() {
    const id = citySelect.value;
    const shipping = prices[id] ? parseFloat(prices[id]) : NaN;
    const shippingText = formatPrice(prices[id]);
    shippingDisplays.forEach(function (el) {
      el.textContent = shippingText;
    });
    if (totalDisplay && !Number.isNaN(subtotal)) {
      const amount = Number.isNaN(shipping) ? subtotal : subtotal + shipping;
      const formatted = formatPrice(amount);
      totalDisplay.textContent = currency ? formatted + " " + currency : formatted;
    }
  }

  function toggleBilling() {
    if (!billingSame || !billingFields) return;
    const hide = billingSame.checked;
    billingFields.style.display = hide ? "none" : "";
    billingFields.querySelectorAll("input").forEach(function (input) {
      input.required = !hide;
    });
  }

  citySelect.addEventListener("change", updateShippingPrice);
  if (billingSame) {
    billingSame.addEventListener("change", toggleBilling);
    toggleBilling();
  }
  updateShippingPrice();
})();
