/**
 * Shop analytics — Chart.js bindings for dashboard canvases.
 */
(function () {
    "use strict";

    var CHART_COLOR = "rgba(201, 169, 98, 0.85)";
    var CHART_FILL = "rgba(201, 169, 98, 0.25)";
    var ORDERS_COLOR = "rgba(30, 77, 99, 0.85)";
    var ORDERS_FILL = "rgba(30, 77, 99, 0.2)";

    function readChartData(scriptId) {
        var el = document.getElementById(scriptId);
        if (!el || !el.textContent) {
            return { labels: [], values: [] };
        }
        try {
            var payload = JSON.parse(el.textContent);
            return {
                labels: payload.labels || [],
                values: payload.values || [],
            };
        } catch (err) {
            return { labels: [], values: [] };
        }
    }

    function legendLabel(canvas) {
        return canvas && canvas.dataset.legendLabel ? canvas.dataset.legendLabel : "";
    }

    function initChart(canvasId, dataId, config) {
        var canvas = document.getElementById(canvasId);
        if (!canvas || typeof Chart === "undefined") {
            return;
        }

        var payload = readChartData(dataId);
        var chartType = config.type || "bar";
        var dataset = {
            label: legendLabel(canvas),
            data: payload.values || [],
            backgroundColor: config.backgroundColor || CHART_COLOR,
            borderColor: config.borderColor || CHART_COLOR,
            borderWidth: 1,
        };

        if (chartType === "line") {
            dataset.fill = true;
            dataset.tension = 0.25;
            dataset.backgroundColor = config.backgroundColor || CHART_FILL;
            dataset.pointRadius = 3;
            dataset.pointHoverRadius = 5;
        }

        new Chart(canvas, {
            type: chartType,
            data: {
                labels: payload.labels || [],
                datasets: [dataset],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: Boolean(dataset.label),
                    },
                },
                scales: config.scales || {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    function initDashboardCharts() {
        if (typeof Chart === "undefined") {
            return;
        }
        initChart("chart-revenue", "chart-revenue-data", {
            type: "line",
            backgroundColor: CHART_FILL,
            borderColor: CHART_COLOR,
        });
        initChart("chart-orders", "chart-orders-data", {
            type: "line",
            backgroundColor: ORDERS_FILL,
            borderColor: ORDERS_COLOR,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 },
                },
            },
        });
        initChart("chart-products", "chart-products-data", {});
        initChart("chart-categories", "chart-categories-data", {});
        initChart("chart-status", "chart-status-data", {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 },
                },
            },
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initDashboardCharts);
    } else {
        initDashboardCharts();
    }
})();
