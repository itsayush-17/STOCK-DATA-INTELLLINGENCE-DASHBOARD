const companySelect = document.getElementById("companySelect");
const periodSelect = document.getElementById("periodSelect");
const compareOne = document.getElementById("compareOne");
const compareTwo = document.getElementById("compareTwo");
const statusMessage = document.getElementById("statusMessage");

let priceChart;
let compareChart;

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(value);

const setStatus = (message, isError = false) => {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("negative", isError);
};

const fillSelect = (select, items, selectedSymbol) => {
  select.innerHTML = "";
  items.forEach((company) => {
    const option = document.createElement("option");
    option.value = company.symbol;
    option.textContent = `${company.symbol} - ${company.name}`;
    option.selected = company.symbol === selectedSymbol;
    select.appendChild(option);
  });
};

const updateSummaryCards = (summary, forecast) => {
  const changeElement = document.getElementById("dayChange");
  const forecastTrendElement = document.getElementById("forecastTrend");
  const changeText = `${summary.price_change >= 0 ? "+" : ""}${formatCurrency(summary.price_change)} (${summary.price_change_pct}%)`;
  const forecastChangeText = `${forecast.trend} (${forecast.projected_change_pct >= 0 ? "+" : ""}${forecast.projected_change_pct}%)`;

  document.getElementById("currentPrice").textContent = formatCurrency(summary.current_price);
  changeElement.textContent = changeText;
  changeElement.className = summary.price_change >= 0 ? "positive" : "negative";
  document.getElementById("periodHigh").textContent = formatCurrency(summary.period_high);
  document.getElementById("periodLow").textContent = formatCurrency(summary.period_low);
  document.getElementById("volatilityScore").textContent = `${summary.volatility_score}%`;
  document.getElementById("lastUpdated").textContent = summary.last_updated;
  document.getElementById("forecastPrice").textContent = formatCurrency(forecast.projected_close);
  forecastTrendElement.textContent = forecastChangeText;
  forecastTrendElement.className = forecast.projected_change_pct >= 0 ? "positive" : "negative";
};

const renderPriceChart = (payload, forecast) => {
  const historyLabels = payload.records.map((item) => item.date);
  const forecastLabels = forecast.forecast.map((item) => item.date);
  const labels = [...historyLabels, ...forecastLabels];
  const closePrices = payload.records.map((item) => item.close);
  const ma7 = payload.records.map((item) => item.ma7);
  const ma20 = payload.records.map((item) => item.ma20);
  const projectedValues = [
    ...new Array(payload.records.length - 1).fill(null),
    payload.records[payload.records.length - 1].close,
    ...forecast.forecast.map((item) => item.close),
  ];

  if (priceChart) {
    priceChart.destroy();
  }

  priceChart = new Chart(document.getElementById("priceChart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: `${payload.symbol} Close`,
          data: [...closePrices, ...new Array(forecast.forecast.length).fill(null)],
          borderColor: "#0d7a5f",
          backgroundColor: "rgba(13, 122, 95, 0.12)",
          fill: true,
          tension: 0.25,
        },
        {
          label: "MA 7",
          data: [...ma7, ...new Array(forecast.forecast.length).fill(null)],
          borderColor: "#c66b2d",
          tension: 0.25,
        },
        {
          label: "MA 20",
          data: [...ma20, ...new Array(forecast.forecast.length).fill(null)],
          borderColor: "#6d4fc2",
          tension: 0.25,
        },
        {
          label: `${forecast.future_days}-Day Projection`,
          data: projectedValues,
          borderColor: "#b85042",
          borderDash: [8, 6],
          tension: 0.25,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
};

const renderCompareChart = (payload) => {
  if (compareChart) {
    compareChart.destroy();
  }

  compareChart = new Chart(document.getElementById("compareChart"), {
    type: "line",
    data: {
      labels: payload.dates,
      datasets: payload.series.map((series, index) => ({
        label: `${series.symbol} Normalized`,
        data: series.values,
        borderColor: index === 0 ? "#0d7a5f" : "#b85042",
        tension: 0.2,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
      scales: {
        y: {
          title: {
            display: true,
            text: "Normalized Index",
          },
        },
      },
    },
  });
};

const fetchJson = async (url) => {
  const response = await fetch(url);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed.");
  }
  return payload;
};

const refreshSingleStockView = async () => {
  const symbol = companySelect.value;
  const days = periodSelect.value;

  setStatus(`Loading ${symbol} market snapshot...`);

  const [summary, series, forecast] = await Promise.all([
    fetchJson(`/api/summary/${symbol}?days=${days}`),
    fetchJson(`/api/data/${symbol}?days=${days}`),
    fetchJson(`/api/forecast/${symbol}?days=${days}&future_days=7`),
  ]);

  updateSummaryCards(summary, forecast);
  renderPriceChart(series, forecast);
  setStatus(`Showing ${symbol} for the last ${days} trading days with a 7-day projection.`);
};

const refreshCompareView = async () => {
  const symbol1 = compareOne.value;
  const symbol2 = compareTwo.value;
  const days = periodSelect.value;

  const comparison = await fetchJson(
    `/api/compare?symbol1=${symbol1}&symbol2=${symbol2}&days=${days}`
  );
  renderCompareChart(comparison);
};

const initializeDashboard = async () => {
  try {
    const companies = await fetchJson("/api/companies");
    fillSelect(companySelect, companies, companies[0].symbol);
    fillSelect(compareOne, companies, companies[0].symbol);
    fillSelect(compareTwo, companies, companies[1].symbol);

    await refreshSingleStockView();
    await refreshCompareView();

    companySelect.addEventListener("change", async () => {
      try {
        await refreshSingleStockView();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    periodSelect.addEventListener("change", async () => {
      try {
        await refreshSingleStockView();
        await refreshCompareView();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    compareOne.addEventListener("change", async () => {
      try {
        await refreshCompareView();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    compareTwo.addEventListener("change", async () => {
      try {
        await refreshCompareView();
      } catch (error) {
        setStatus(error.message, true);
      }
    });
  } catch (error) {
    setStatus(error.message, true);
  }
};

initializeDashboard();
