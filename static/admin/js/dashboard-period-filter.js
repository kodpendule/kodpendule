/**
 * Shop analytics — show quick or manual period fields based on dropdown.
 */
(function () {
    "use strict";

    function initDashboardPeriodFilter() {
        var form = document.getElementById("dashboard-period-form");
        var modeSelect = document.getElementById("id_filter_mode");
        if (!form || !modeSelect) {
            return;
        }

        var panels = form.querySelectorAll("[data-filter-panel]");

        function syncPanels() {
            var mode = modeSelect.value;
            panels.forEach(function (panel) {
                var active = panel.getAttribute("data-filter-panel") === mode;
                panel.hidden = !active;
                panel.querySelectorAll("input, select").forEach(function (field) {
                    field.disabled = !active;
                });
            });
        }

        modeSelect.addEventListener("change", syncPanels);
        syncPanels();
    }

    document.addEventListener("DOMContentLoaded", initDashboardPeriodFilter);
})();
