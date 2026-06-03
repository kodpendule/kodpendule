/**
 * Cart — AJAX add-to-cart, mini-cart drawer, live quantity updates.
 */
(function () {
    "use strict";

    var TOAST_MS = 4200;
    var FAB_MS = 420;

    function getGlobalCsrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }

    function getCsrfToken(form) {
        var input = form.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : getGlobalCsrfToken();
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function isFabPageHidden() {
        return !!document.querySelector(".shop-page--cart, .shop-page--checkout");
    }

    function getCartDrawer() {
        return document.getElementById("shopCartDrawer");
    }

    function hideDrawerLoading(drawer) {
        var el = drawer
            ? drawer.querySelector("[data-cart-drawer-loading]")
            : null;
        if (el) {
            el.hidden = true;
        }
    }

    function maybeCloseDrawer() {
        var drawer = getCartDrawer();
        if (!drawer || typeof bootstrap === "undefined") {
            return;
        }
        var instance = bootstrap.Offcanvas.getInstance(drawer);
        if (instance) {
            instance.hide();
        }
    }

    function bindQtyControls(root) {
        if (!root) {
            return;
        }
        root.querySelectorAll("[data-shop-qty]").forEach(function (wrap) {
            var input = wrap.querySelector("input[type='number']");
            var inc = wrap.querySelector("[data-shop-qty-inc]");
            var dec = wrap.querySelector("[data-shop-qty-dec]");
            if (!input || !inc || !dec || wrap.dataset.qtyBound === "1") {
                return;
            }
            wrap.dataset.qtyBound = "1";

            var min = parseInt(input.getAttribute("min") || "1", 10);
            var max = parseInt(input.getAttribute("max") || "9999", 10);

            function setValue(next) {
                var v = Math.min(max, Math.max(min, next));
                if (Number.isNaN(v)) {
                    v = min;
                }
                input.value = String(v);
                input.dispatchEvent(new Event("change", { bubbles: true }));
            }

            inc.addEventListener("click", function () {
                setValue(parseInt(input.value || String(min), 10) + 1);
            });
            dec.addEventListener("click", function () {
                setValue(parseInt(input.value || String(min), 10) - 1);
            });
            input.addEventListener("input", function () {
                var v = parseInt(input.value || String(min), 10);
                if (Number.isNaN(v)) {
                    return;
                }
                setValue(v);
            });
        });
    }

    function renderCartDrawer(data) {
        var drawer = getCartDrawer();
        if (!drawer) {
            return;
        }

        var linesEl = drawer.querySelector("[data-cart-drawer-lines]");
        var emptyEl = drawer.querySelector("[data-cart-drawer-empty]");
        var footerEl = drawer.querySelector("[data-cart-drawer-footer]");
        var subtotalEl = drawer.querySelector("[data-cart-drawer-subtotal]");
        var loadingEl = drawer.querySelector("[data-cart-drawer-loading]");
        var openLink = drawer.querySelector("[data-cart-drawer-open-link]");
        var csrf = getGlobalCsrfToken();
        var decLabel = drawer.getAttribute("data-i18n-dec") || "Decrease quantity";
        var incLabel = drawer.getAttribute("data-i18n-inc") || "Increase quantity";
        var qtyLabel = drawer.getAttribute("data-i18n-qty") || "Quantity";
        var removeLabel = drawer.getAttribute("data-i18n-remove") || "Remove";

        hideDrawerLoading(drawer);

        if (!linesEl || !emptyEl || !footerEl) {
            return;
        }

        if (openLink && drawer.getAttribute("data-cart-detail-url")) {
            openLink.href = drawer.getAttribute("data-cart-detail-url");
        }

        if (!data.item_count) {
            linesEl.innerHTML = "";
            emptyEl.hidden = false;
            footerEl.hidden = true;
            return;
        }

        emptyEl.hidden = true;
        footerEl.hidden = false;
        if (subtotalEl && data.subtotal_display) {
            subtotalEl.textContent = data.subtotal_display;
        }

        linesEl.innerHTML = (data.lines || [])
            .map(function (line) {
                var media = line.image_url
                    ? '<img src="' + escapeHtml(line.image_url) + '" alt="" loading="lazy">'
                    : '<span class="shop-cart-drawer-line__media--placeholder" aria-hidden="true"></span>';
                return (
                    '<li class="shop-cart-drawer-line" data-cart-drawer-line data-product-id="' +
                    escapeHtml(line.product_id) +
                    '">' +
                    '<a class="shop-cart-drawer-line__media" href="' +
                    escapeHtml(line.url) +
                    '">' +
                    media +
                    "</a>" +
                    '<div class="shop-cart-drawer-line__body">' +
                    '<a class="shop-cart-drawer-line__name" href="' +
                    escapeHtml(line.url) +
                    '">' +
                    escapeHtml(line.name) +
                    "</a>" +
                    '<p class="shop-cart-drawer-line__unit">' +
                    escapeHtml(line.unit_price_display) +
                    "</p>" +
                    '<form method="post" action="' +
                    escapeHtml(line.update_url) +
                    '" class="shop-cart-drawer-line__qty-form" data-shop-cart-drawer-qty>' +
                    '<input type="hidden" name="csrfmiddlewaretoken" value="' +
                    escapeHtml(csrf) +
                    '">' +
                    '<div class="shop-qty shop-qty--compact" data-shop-qty>' +
                    '<button class="shop-qty__btn" type="button" data-shop-qty-dec aria-label="' +
                    escapeHtml(decLabel) +
                    '">−</button>' +
                    '<input type="number" name="quantity" value="' +
                    escapeHtml(line.quantity) +
                    '" min="1" max="' +
                    escapeHtml(line.stock) +
                    '" class="shop-qty__input" inputmode="numeric" aria-label="' +
                    escapeHtml(qtyLabel) +
                    '">' +
                    '<button class="shop-qty__btn" type="button" data-shop-qty-inc aria-label="' +
                    escapeHtml(incLabel) +
                    '">+</button>' +
                    "</div>" +
                    "</form>" +
                    '<div class="shop-cart-drawer-line__footer">' +
                    '<p class="shop-cart-drawer-line__total" data-cart-drawer-line-total>' +
                    escapeHtml(line.line_total_display) +
                    "</p>" +
                    (line.remove_url
                        ? '<form method="post" action="' +
                          escapeHtml(line.remove_url) +
                          '" class="shop-cart-drawer-line__remove-form" data-shop-cart-drawer-remove>' +
                          '<input type="hidden" name="csrfmiddlewaretoken" value="' +
                          escapeHtml(csrf) +
                          '">' +
                          '<button type="submit" class="shop-btn shop-btn--ghost shop-btn--sm">' +
                          escapeHtml(removeLabel) +
                          "</button></form>"
                        : "") +
                    "</div>" +
                    "</div>" +
                    "</li>"
                );
            })
            .join("");

        bindQtyControls(linesEl);
    }

    function updateCartDrawerInPlace(data) {
        var drawer = getCartDrawer();
        if (!drawer) {
            return;
        }

        hideDrawerLoading(drawer);

        var linesEl = drawer.querySelector("[data-cart-drawer-lines]");
        var emptyEl = drawer.querySelector("[data-cart-drawer-empty]");
        var footerEl = drawer.querySelector("[data-cart-drawer-footer]");
        var subtotalEl = drawer.querySelector("[data-cart-drawer-subtotal]");

        if (!linesEl || !emptyEl || !footerEl) {
            renderCartDrawer(data);
            return;
        }

        if (!data.item_count) {
            renderCartDrawer(data);
            return;
        }

        emptyEl.hidden = true;
        footerEl.hidden = false;
        if (subtotalEl && data.subtotal_display) {
            subtotalEl.textContent = data.subtotal_display;
        }

        var linesById = {};
        (data.lines || []).forEach(function (line) {
            linesById[String(line.product_id)] = line;
        });

        var needsFullRender = false;
        linesEl.querySelectorAll("[data-cart-drawer-line]").forEach(function (row) {
            if (!row.querySelector("[data-shop-cart-drawer-remove]")) {
                needsFullRender = true;
            }
            var productId = row.getAttribute("data-product-id");
            var line = linesById[productId];
            if (!line) {
                row.remove();
                return;
            }
            delete linesById[productId];

            var totalEl = row.querySelector("[data-cart-drawer-line-total]");
            if (totalEl && line.line_total_display) {
                totalEl.textContent = line.line_total_display;
            }
            var input = row.querySelector('input[name="quantity"]');
            if (input) {
                if (String(input.value) !== String(line.quantity)) {
                    input.value = String(line.quantity);
                }
                if (String(input.getAttribute("max") || "") !== String(line.stock)) {
                    input.setAttribute("max", String(line.stock));
                }
            }
        });

        if (Object.keys(linesById).length > 0) {
            needsFullRender = true;
        }

        if (needsFullRender || !linesEl.querySelector("[data-cart-drawer-line]")) {
            renderCartDrawer(data);
        }
    }

    function fetchCartState() {
        var drawer = getCartDrawer();
        if (!drawer) {
            return Promise.resolve(null);
        }
        var url = drawer.getAttribute("data-cart-state-url");
        if (!url) {
            return Promise.resolve(null);
        }
        var loadingEl = drawer.querySelector("[data-cart-drawer-loading]");
        if (loadingEl) {
            loadingEl.hidden = false;
        }
        return fetch(url, {
            method: "GET",
            headers: {
                Accept: "application/json",
                "X-Requested-With": "XMLHttpRequest",
            },
            credentials: "same-origin",
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data && data.ok) {
                    applyCartState(data);
                }
                return data;
            })
            .catch(function () {
                return null;
            })
            .finally(function () {
                hideDrawerLoading(drawer);
            });
    }

    function removeFromDrawer(form) {
        var drawer = getCartDrawer();
        if (!drawer) {
            return;
        }
        var row = form.closest("[data-cart-drawer-line]");
        if (row) {
            row.classList.add("is-updating");
        }
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
                    showDrawerLineError(
                        form,
                        (result.data && result.data.error) ||
                            "Unable to update cart."
                    );
                    return;
                }
                applyCartState(result.data);
            })
            .catch(function () {
                showDrawerLineError(form, "Unable to update cart.");
            })
            .finally(function () {
                if (row) {
                    row.classList.remove("is-updating");
                }
            });
    }

    function showDrawerLineError(form, message) {
        var row = form.closest("[data-cart-drawer-line]");
        if (!row) {
            return;
        }
        var existing = row.querySelector("[data-cart-drawer-line-error]");
        if (existing) {
            existing.remove();
        }
        var alert = document.createElement("p");
        alert.className = "shop-cart-drawer-line__error";
        alert.setAttribute("data-cart-drawer-line-error", "");
        alert.setAttribute("role", "alert");
        alert.textContent = message;
        row.appendChild(alert);
        window.setTimeout(function () {
            alert.remove();
        }, 4000);
    }

    function updateCartFromDrawer(form) {
        var drawer = getCartDrawer();
        if (!drawer) {
            return;
        }
        var row = form.closest("[data-cart-drawer-line]");
        if (row) {
            row.classList.add("is-updating");
        }
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
                    showDrawerLineError(
                        form,
                        (result.data && result.data.error) ||
                            "Unable to update cart."
                    );
                    return;
                }
                applyCartState(result.data);
            })
            .catch(function () {
                showDrawerLineError(form, "Unable to update cart.");
            })
            .finally(function () {
                if (row) {
                    row.classList.remove("is-updating");
                }
            });
    }

    function syncFloatingCart(data, options) {
        options = options || {};
        var fab = document.getElementById("shopCartFab");
        if (!fab) {
            return;
        }

        if (isFabPageHidden()) {
            fab.classList.remove("is-visible", "is-added");
            fab.hidden = true;
            return;
        }

        var count = data.item_count || 0;
        var visible = fab.classList.contains("is-visible");

        if (data.item_count_label) {
            fab.setAttribute("aria-label", data.item_count_label);
        }

        if (count > 0) {
            if (!visible) {
                fab.hidden = false;
                window.requestAnimationFrame(function () {
                    fab.classList.add("is-visible");
                });
            }
            if (options.justAdded) {
                fab.classList.remove("is-added");
                window.requestAnimationFrame(function () {
                    fab.classList.add("is-added");
                    window.setTimeout(function () {
                        fab.classList.remove("is-added");
                    }, 560);
                });
            }
        } else if (visible || !fab.hidden) {
            fab.classList.remove("is-visible", "is-added");
            maybeCloseDrawer();
            window.setTimeout(function () {
                if (!fab.classList.contains("is-visible")) {
                    fab.hidden = true;
                }
            }, FAB_MS);
        } else {
            fab.hidden = true;
            fab.classList.remove("is-visible", "is-added");
        }
    }

    function applyCartState(data, options) {
        document.querySelectorAll("[data-cart-header-count]").forEach(function (badge) {
            if (data.item_count > 0) {
                badge.textContent = String(data.item_count);
                badge.hidden = false;
            } else {
                badge.hidden = true;
            }
        });

        syncFloatingCart(data, options);

        var drawer = getCartDrawer();
        if (drawer && drawer.querySelector("[data-cart-drawer-line]")) {
            updateCartDrawerInPlace(data);
        } else if (drawer) {
            renderCartDrawer(data);
        }

        var root = document.querySelector("[data-cart-page]");
        if (!root) {
            return;
        }

        var subtotalEl = root.querySelector("[data-cart-subtotal]");
        var summaryEl = root.querySelector("[data-cart-header-summary]");
        if (subtotalEl && data.subtotal_display) {
            subtotalEl.textContent = data.subtotal_display;
        }
        if (summaryEl && data.item_count_label) {
            summaryEl.textContent = data.item_count_label;
        }

        (data.lines || []).forEach(function (line) {
            var row = root.querySelector(
                '[data-cart-line][data-product-id="' + line.product_id + '"]'
            );
            if (!row) {
                if (data.item_count === 0) {
                    window.location.reload();
                }
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

    function getToastRoot() {
        var root = document.getElementById("shop-toast-root");
        if (root) {
            return root;
        }
        root = document.createElement("div");
        root.id = "shop-toast-root";
        root.className = "shop-toast-root";
        root.setAttribute("aria-live", "polite");
        root.setAttribute("aria-atomic", "true");
        document.body.appendChild(root);
        return root;
    }

    function showToast(message, type) {
        if (!message) {
            return;
        }
        var root = getToastRoot();
        var toast = document.createElement("p");
        toast.className = "shop-toast shop-toast--" + (type || "success");
        toast.setAttribute("role", "status");
        toast.textContent = message;
        root.appendChild(toast);
        window.requestAnimationFrame(function () {
            toast.classList.add("is-visible");
        });
        window.setTimeout(function () {
            toast.classList.remove("is-visible");
            window.setTimeout(function () {
                toast.remove();
            }, 300);
        }, TOAST_MS);
    }

    function setSubmitBusy(btn, busy) {
        if (!btn) {
            return;
        }
        btn.disabled = busy;
        btn.classList.toggle("is-loading", busy);
        btn.setAttribute("aria-busy", busy ? "true" : "false");
    }

    function initCartDrawer() {
        var drawer = getCartDrawer();
        if (!drawer) {
            return;
        }

        drawer.addEventListener("shown.bs.offcanvas", function () {
            fetchCartState();
        });

        drawer.addEventListener("change", function (event) {
            var form = event.target.closest("[data-shop-cart-drawer-qty]");
            if (form && event.target.name === "quantity") {
                updateCartFromDrawer(form);
            }
        });

        drawer.addEventListener("submit", function (event) {
            var form = event.target.closest("[data-shop-cart-drawer-remove]");
            if (!form) {
                return;
            }
            event.preventDefault();
            removeFromDrawer(form);
        });
    }

    function initAddToCart() {
        document.querySelectorAll("form[data-shop-add-cart]").forEach(function (form) {
            form.addEventListener("submit", function (event) {
                event.preventDefault();
                var btn = form.querySelector('button[type="submit"]');
                if (!btn || btn.disabled) {
                    return;
                }

                setSubmitBusy(btn, true);
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
                            showToast(
                                (result.data && result.data.error) ||
                                    "Unable to add to cart.",
                                "error"
                            );
                            return;
                        }
                        applyCartState(result.data, { justAdded: true });
                        showToast(result.data.message, "success");
                    })
                    .catch(function () {
                        showToast("Unable to add to cart.", "error");
                    })
                    .finally(function () {
                        setSubmitBusy(btn, false);
                    });
            });
        });
    }

    function initCartPage() {
        var root = document.querySelector("[data-cart-page]");
        if (!root) {
            return;
        }

        var forms = root.querySelectorAll("[data-shop-cart-qty]");
        var pending = 0;

        function setBusy(isBusy) {
            root.classList.toggle("is-cart-updating", isBusy);
        }

        function showLineError(form, message) {
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
                        showLineError(
                            form,
                            (result.data && result.data.error) ||
                                "Unable to update cart."
                        );
                        return;
                    }
                    applyCartState(result.data);
                })
                .catch(function () {
                    showLineError(form, "Unable to update cart.");
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

    function initFloatingCart() {
        var fab = document.getElementById("shopCartFab");
        if (!fab) {
            return;
        }

        if (isFabPageHidden()) {
            fab.hidden = true;
            fab.classList.remove("is-visible", "is-added");
            return;
        }

        var badge = fab.querySelector("[data-cart-header-count]");
        var count = 0;
        if (badge && !badge.hidden && badge.textContent) {
            count = parseInt(badge.textContent, 10) || 0;
        }

        if (count > 0) {
            fab.hidden = false;
            fab.classList.add("is-visible");
        } else {
            fab.hidden = true;
            fab.classList.remove("is-visible", "is-added");
        }
    }

    function init() {
        initFloatingCart();
        initCartDrawer();
        initAddToCart();
        initCartPage();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
