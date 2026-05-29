/**
 * Changelist helpers — select-all fallback when Django actions.js cannot bind.
 */
(function () {
    "use strict";

    function initSelectAll() {
        var toggle = document.getElementById("action-toggle");
        var boxes = document.querySelectorAll(
            "#result_list tbody input.action-select"
        );
        if (!toggle || !boxes.length) {
            return;
        }

        if (toggle.dataset.kpSelectAllBound === "1") {
            return;
        }
        toggle.dataset.kpSelectAllBound = "1";

        toggle.addEventListener("change", function () {
            var checked = toggle.checked;
            boxes.forEach(function (box) {
                box.checked = checked;
                var row = box.closest("tr");
                if (row) {
                    row.classList.toggle("selected", checked);
                }
            });
            var counter = document.querySelector("span.action-counter");
            if (counter && counter.dataset.actionsIcnt) {
                var total = Number(counter.dataset.actionsIcnt);
                var sel = checked ? total : 0;
                counter.textContent = sel + " od " + total + " izabrano";
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initSelectAll);
    } else {
        initSelectAll();
    }
})();
