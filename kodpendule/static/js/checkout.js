(function () {
  const citySelect = document.getElementById("id_shipping_city");
  const priceDisplay = document.getElementById("shipping-price-display");
  const billingSame = document.getElementById("id_billing_same");
  const billingFields = document.getElementById("billing-fields");
  const pricesEl = document.getElementById("city-prices-data");

  if (!pricesEl || !citySelect) {
    return;
  }

  const prices = JSON.parse(pricesEl.textContent);

  function formatPrice(value) {
    if (!value) return "—";
    const num = parseFloat(value);
    if (Number.isNaN(num)) return "—";
    return num.toLocaleString("sr-RS", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function updateShippingPrice() {
    const id = citySelect.value;
    if (priceDisplay) {
      priceDisplay.textContent = formatPrice(prices[id]);
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
