/**
 * Cart page — auto-update quantities via AJAX (backend-authoritative totals).
 */
(function () {
    "use strict";

    function getCsrfToken(form) {
        var input = form.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : "";
    }

    function initCartPage() {
        var root = document.querySelector("[data-cart-page]");
        if (!root) {
            return;
        }

        var subtotalEl = root.querySelector("[data-cart-subtotal]");
        var summaryEl = root.querySelector("[data-cart-header-summary]");
        var headerBadge = document.querySelector("[data-cart-header-count]");
        var forms = root.querySelectorAll("[data-shop-cart-qty]");
        var pending = 0;

        function setBusy(isBusy) {
            root.classList.toggle("is-cart-updating", isBusy);
        }

        function applyState(data) {
            if (subtotalEl && data.subtotal_display) {
                subtotalEl.textContent = data.subtotal_display;
            }
            if (summaryEl && data.item_count_label) {
                summaryEl.textContent = data.item_count_label;
            }
            if (headerBadge) {
                if (data.item_count > 0) {
                    headerBadge.textContent = String(data.item_count);
                    headerBadge.hidden = false;
                } else {
                    headerBadge.hidden = true;
                }
            }
            (data.lines || []).forEach(function (line) {
                var row = root.querySelector(
                    '[data-cart-line][data-product-id="' + line.product_id + '"]'
                );
                if (!row) {
                    return;
                }
                var totalEl = row.querySelector("[data-cart-line-total]");
                if (totalEl && line.line_total_display) {
                    totalEl.textContent = line.line_total_display;
                }
                var input = row.querySelector('input[name="quantity"]');
                if (input && String(input.value) !== String(line.quantity)) {
                    input.value = String(line.quantity);
                }
            });
        }

        function showError(form, message) {
            var row = form.closest("[data-cart-line]");
            if (!row) {
                return;
            }
            var existing = row.querySelector("[data-cart-line-error]");
            if (existing) {
                existing.remove();
            }
            var alert = document.createElement("p");
            alert.className = "shop-cart-line__error";
            alert.setAttribute("data-cart-line-error", "");
            alert.setAttribute("role", "alert");
            alert.textContent = message;
            row.querySelector(".shop-cart-line__actions").appendChild(alert);
            window.setTimeout(function () {
                alert.remove();
            }, 4000);
        }

        function updateCart(form) {
            pending += 1;
            setBusy(true);
            var body = new FormData(form);

            fetch(form.action, {
                method: "POST",
                body: body,
                headers: {
                    Accept: "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                },
                credentials: "same-origin",
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, data: data };
                    });
                })
                .then(function (result) {
                    if (!result.ok || !result.data.ok) {
                        showError(
                            form,
                            (result.data && result.data.error) ||
                                "Unable to update cart."
                        );
                        return;
                    }
                    applyState(result.data);
                })
                .catch(function () {
                    showError(form, "Unable to update cart.");
                })
                .finally(function () {
                    pending -= 1;
                    if (pending <= 0) {
                        pending = 0;
                        setBusy(false);
                    }
                });
        }

        forms.forEach(function (form) {
            var input = form.querySelector('input[name="quantity"]');
            if (!input) {
                return;
            }

            input.addEventListener("change", function () {
                updateCart(form);
            });
        });
    }

    document.addEventListener("DOMContentLoaded", initCartPage);
})();
