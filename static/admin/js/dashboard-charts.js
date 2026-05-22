(function () {
  "use strict";

  function readChartData(elementId) {
    var el = document.getElementById(elementId);
    if (!el || !el.textContent) {
      return { labels: [], values: [] };
    }
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return { labels: [], values: [] };
    }
  }

  function hasChartJs() {
    return typeof window.Chart !== "undefined";
  }

  function legendLabel(canvas) {
    return (canvas && canvas.dataset.legendLabel) || "";
  }

  function lineChart(canvasId, dataId) {
    var canvas = document.getElementById(canvasId);
    var data = readChartData(dataId);
    if (!canvas || !hasChartJs() || !data.labels.length) {
      return;
    }
    var label = legendLabel(canvas);
    new Chart(canvas, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: label,
            data: data.values,
            borderColor: "#417690",
            backgroundColor: "rgba(65, 118, 144, 0.15)",
            fill: true,
            tension: 0.25,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true },
        },
      },
    });
  }

  function barChart(canvasId, dataId) {
    var canvas = document.getElementById(canvasId);
    var data = readChartData(dataId);
    if (!canvas || !hasChartJs() || !data.labels.length) {
      return;
    }
    var label = legendLabel(canvas);
    new Chart(canvas, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: label,
            data: data.values,
            backgroundColor: "#79aec8",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        indexAxis: data.labels.length > 6 ? "y" : "x",
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true },
          y: { beginAtZero: true },
        },
      },
    });
  }

  function doughnutChart(canvasId, dataId) {
    var canvas = document.getElementById(canvasId);
    var data = readChartData(dataId);
    if (!canvas || !hasChartJs() || !data.labels.length) {
      return;
    }
    new Chart(canvas, {
      type: "doughnut",
      data: {
        labels: data.labels,
        datasets: [
          {
            data: data.values,
            backgroundColor: [
              "#6c757d",
              "#0d6efd",
              "#198754",
              "#ffc107",
              "#dc3545",
              "#0dcaf0",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
      },
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    lineChart("chart-revenue", "chart-revenue-data");
    barChart("chart-products", "chart-products-data");
    barChart("chart-categories", "chart-categories-data");
    doughnutChart("chart-status", "chart-status-data");
  });
})();
