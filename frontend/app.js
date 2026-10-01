/**
 * Smart Wealth Intelligence - Frontend Application Logic
 * Multi-tab navigation, financial glossary, interactive tooltips, and analytics rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global state store
  let currentProfileData = null;
  let chartInstances = {};

  // Glossary Data Dictionary
  const glossaryData = [
    {
      term: "SIP (Systematic Investment Plan)",
      category: "basics",
      def: "A method of investing a fixed rupee amount into a mutual fund at regular intervals (usually monthly).",
      analogy: "💡 Like a monthly gym subscription for your savings — you build wealth steadily without worrying about timing the market."
    },
    {
      term: "Asset Allocation",
      category: "basics",
      def: "Dividing your total investment capital among different asset buckets like Stocks, Gold, Debt/FDs, and Cash.",
      analogy: "💡 Don't put all your eggs in one basket. If stock markets drop, your Gold and FD reserves keep your net worth safe."
    },
    {
      term: "Emergency Fund",
      category: "basics",
      def: "A cash reserve equivalent to 3 to 6 months of living expenses held in liquid bank accounts or fixed deposits.",
      analogy: "💡 A financial shock-absorber so unexpected medical bills or job transitions never force you to sell long-term stocks at a loss."
    },
    {
      term: "Portfolio Health Score",
      category: "risk",
      def: "A composite 0-100 diagnostic score assessing your asset mix, risk alignment, emergency safety buffer, and diversification.",
      analogy: "💡 A regular health report card for your money: 80+ means excellent fitness, while below 50 means time for a check-up!"
    },
    {
      term: "Monte Carlo Simulation",
      category: "advanced",
      def: "A statistical modeling technique that runs 1,000 randomized future market scenarios to calculate realistic wealth ranges.",
      analogy: "💡 Like playing 1,000 simulated games of chess to see your best-case, average, and worst-case outcomes over 10 years."
    },
    {
      term: "Market Regime",
      category: "advanced",
      def: "The overall prevailing climate of financial markets (e.g. Bullish, Fairly Valued, Overvalued, or High Volatility).",
      analogy: "💡 The market weather report! Helps you decide whether to wear a raincoat (hold cash/FDs) or enjoy the sun (invest in equities)."
    },
    {
      term: "CAGR (Compound Annual Growth Rate)",
      category: "basics",
      def: "The geometric mean return rate that provides a constant annual rate of return over a multi-year investment period.",
      analogy: "💡 The true average speed your money grew year-after-year with compounding interest."
    },
    {
      term: "Equity (Stocks)",
      category: "assets",
      def: "Buying shares of real ownership in companies (e.g., Reliance, TCS, HDFC). High growth potential over long periods.",
      analogy: "💡 Becoming a mini-partner in top businesses and sharing in their future profit growth."
    },
    {
      term: "Debt & Fixed Income",
      category: "assets",
      def: "Lending money to governments or top corporations in exchange for fixed, guaranteed interest payments (e.g. FDs, Bonds).",
      analogy: "💡 A reliable rental income stream that guarantees capital preservation with low volatility."
    },
    {
      term: "Gold & Precious Metals",
      category: "assets",
      def: "A physical or digital store of value that historically protects wealth against currency inflation and geopolitical crises.",
      analogy: "💡 An insurance policy for your portfolio when global financial uncertainty rises."
    },
    {
      term: "Rebalancing",
      category: "risk",
      def: "Selling a portion of asset classes that grew too large and buying underperforming ones to restore your target allocation.",
      analogy: "💡 Trimming high-growing branches of a tree to keep the whole garden balanced and healthy."
    },
    {
      term: "Diversification Score",
      category: "risk",
      def: "A rating measuring how well your money is distributed across uncorrelated assets and different industry sectors.",
      analogy: "💡 Ensuring you own both umbrellas (gold/bonds) and sunglasses (stocks) so you profit in any weather."
    }
  ];

  // DOM Elements
  const personaSelect = document.getElementById("personaSelect");
  const btnRecalculate = document.getElementById("btnRecalculate");
  const profileForm = document.getElementById("profileForm");

  // Form Inputs
  const inputName = document.getElementById("inputName");
  const inputAge = document.getElementById("inputAge");
  const inputHorizon = document.getElementById("inputHorizon");
  const inputIncome = document.getElementById("inputIncome");
  const inputExpenses = document.getElementById("inputExpenses");
  const inputEmergency = document.getElementById("inputEmergency");
  const inputStability = document.getElementById("inputStability");
  const valStability = document.getElementById("valStability");
  const inputLossTolerance = document.getElementById("inputLossTolerance");
  const valLossTolerance = document.getElementById("valLossTolerance");

  // Goals
  const goalsListContainer = document.getElementById("goalsListContainer");
  const btnAddGoal = document.getElementById("btnAddGoal");
  const goalModal = document.getElementById("goalModal");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnCancelGoal = document.getElementById("btnCancelGoal");
  const addGoalForm = document.getElementById("addGoalForm");

  // Term Modal Elements
  const termModal = document.getElementById("termExplanationModal");
  const btnCloseExpModal = document.getElementById("btnCloseExpModal");
  const expModalTermTitle = document.getElementById("expModalTermTitle");
  const expModalDef = document.getElementById("expModalDef");
  const expModalAnalogy = document.getElementById("expModalAnalogy");

  // Currency Formatters
  function formatINR(val) {
    if (val === undefined || val === null || isNaN(val)) return "₹0";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0
    }).format(val);
  }

  function formatCompactINR(val) {
    if (!val || isNaN(val)) return "₹0";
    if (val >= 10000000) {
      return `₹${(val / 10000000).toFixed(2)} Cr`;
    } else if (val >= 100000) {
      return `₹${(val / 100000).toFixed(2)} L`;
    }
    return formatINR(val);
  }

  // Application Initialization
  async function init() {
    setupNavigationTabs();
    setupEventListeners();
    setupGlossaryAndTooltips();
    await fetchBootstrap();
  }

  // 1. Navigation Tab Switching
  function setupNavigationTabs() {
    const tabBtns = document.querySelectorAll(".nav-tab-btn");
    const pages = document.querySelectorAll(".tab-page");

    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetTab = btn.getAttribute("data-tab");

        tabBtns.forEach((b) => b.classList.remove("active"));
        pages.forEach((p) => p.classList.remove("active"));

        btn.classList.add("active");
        const activePage = document.getElementById(targetTab);
        if (activePage) activePage.classList.add("active");
      });
    });
  }

  // 2. Global Event Listeners
  function setupEventListeners() {
    // Slider values
    inputStability.addEventListener("input", (e) => { valStability.textContent = e.target.value; });
    inputLossTolerance.addEventListener("input", (e) => { valLossTolerance.textContent = e.target.value; });

    // Persona Selector
    personaSelect.addEventListener("change", async (e) => {
      const selectedId = e.target.value;
      if (!currentProfileData || !currentProfileData.preset_personas) return;
      const personaObj = currentProfileData.preset_personas.find((p) => p.id === selectedId);
      if (personaObj && personaObj.profile) {
        populateForm(personaObj.profile);
        await recalculatePlan();
      }
    });

    // Form submission & recalculation
    btnRecalculate.addEventListener("click", (e) => {
      e.preventDefault();
      recalculatePlan();
    });

    profileForm.addEventListener("submit", (e) => {
      e.preventDefault();
      recalculatePlan();
    });

    // Modal Goal Handlers
    btnAddGoal.addEventListener("click", () => { goalModal.classList.add("active"); });
    btnCloseModal.addEventListener("click", () => { goalModal.classList.remove("active"); });
    btnCancelGoal.addEventListener("click", () => { goalModal.classList.remove("active"); });

    addGoalForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const newGoal = {
        id: "g_" + Date.now(),
        name: document.getElementById("newGoalName").value,
        target_amount: parseFloat(document.getElementById("newGoalTarget").value),
        timeline_years: parseFloat(document.getElementById("newGoalYears").value),
        expected_return_pct: parseFloat(document.getElementById("newGoalReturn").value),
        priority: document.getElementById("newGoalPriority").value
      };

      if (!currentProfileData.profile.goals) currentProfileData.profile.goals = [];
      currentProfileData.profile.goals.push(newGoal);
      goalModal.classList.remove("active");
      addGoalForm.reset();
      recalculatePlan();
    });

    // Term Explanation Modal Close
    if (btnCloseExpModal) {
      btnCloseExpModal.addEventListener("click", () => {
        termModal.classList.remove("active");
      });
    }
  }

  // 3. Glossary Rendering & Search
  function setupGlossaryAndTooltips() {
    const gridContainer = document.getElementById("glossaryGridContainer");
    const searchInput = document.getElementById("glossarySearchInput");
    const pillBtns = document.querySelectorAll(".pill-btn");

    function renderGlossary(filterText = "", category = "all") {
      if (!gridContainer) return;
      gridContainer.innerHTML = "";

      const filtered = glossaryData.filter((item) => {
        const matchesCat = category === "all" || item.category === category;
        const matchesText = item.term.toLowerCase().includes(filterText.toLowerCase()) ||
                            item.def.toLowerCase().includes(filterText.toLowerCase());
        return matchesCat && matchesText;
      });

      if (filtered.length === 0) {
        gridContainer.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem; grid-column: 1 / -1;">No matching financial terms found.</p>`;
        return;
      }

      filtered.forEach((item) => {
        const card = document.createElement("div");
        card.className = "glossary-card";
        card.innerHTML = `
          <div class="glossary-term-title">
            <span>${item.term}</span>
            <span class="badge badge-info" style="font-size:0.7rem;">${item.category}</span>
          </div>
          <p class="glossary-def">${item.def}</p>
          <div class="glossary-analogy">${item.analogy}</div>
        `;
        gridContainer.appendChild(card);
      });
    }

    // Search event
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        const activePill = document.querySelector(".pill-btn.active");
        const cat = activePill ? activePill.getAttribute("data-category") : "all";
        renderGlossary(e.target.value, cat);
      });
    }

    // Category pills
    pillBtns.forEach((pill) => {
      pill.addEventListener("click", () => {
        pillBtns.forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");
        const cat = pill.getAttribute("data-category");
        const query = searchInput ? searchInput.value : "";
        renderGlossary(query, cat);
      });
    });

    renderGlossary();

    // Attach click handlers to any [?] tooltips across the UI
    document.addEventListener("click", (e) => {
      const tooltip = e.target.closest(".term-tooltip");
      if (tooltip) {
        const termName = tooltip.getAttribute("data-term");
        showTermModal(termName);
      }
    });
  }

  function showTermModal(termName) {
    const item = glossaryData.find((g) => g.term.toLowerCase().includes(termName.toLowerCase())) || {
      term: termName,
      def: "A financial parameter used in portfolio modeling and wealth management.",
      analogy: "💡 Check the Financial Glossary tab for more details."
    };

    expModalTermTitle.innerHTML = `<i class="fa-solid fa-lightbulb text-amber"></i> ${item.term}`;
    expModalDef.textContent = item.def;
    expModalAnalogy.textContent = item.analogy;
    termModal.classList.add("active");
  }

  // API Requests
  async function fetchBootstrap() {
    try {
      const res = await fetch("/api/bootstrap");
      const data = await res.json();
      currentProfileData = data;
      populateForm(data.profile);
      renderDashboard(data);
    } catch (err) {
      console.error("Failed to fetch bootstrap analytics:", err);
    }
  }

  async function recalculatePlan() {
    const payload = extractFormData();
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      currentProfileData = data;
      renderDashboard(data);
    } catch (err) {
      console.error("Failed to recalculate analytics:", err);
    }
  }

  function populateForm(profile) {
    if (!profile) return;
    inputName.value = profile.name || "Investor";
    inputAge.value = profile.age || 30;
    inputHorizon.value = profile.horizon_years || 15;
    inputIncome.value = profile.monthly_income || 150000;
    inputExpenses.value = profile.monthly_expenses || 80000;
    inputEmergency.value = profile.current_emergency_reserve || 300000;

    const stab = profile.income_stability_score || 8;
    inputStability.value = stab;
    valStability.textContent = stab;

    const loss = profile.loss_tolerance_score || 7;
    inputLossTolerance.value = loss;
    valLossTolerance.textContent = loss;
  }

  function extractFormData() {
    const existingGoals = (currentProfileData && currentProfileData.profile) ? (currentProfileData.profile.goals || []) : [];
    const existingPortfolio = (currentProfileData && currentProfileData.profile) ? (currentProfileData.profile.current_portfolio || {}) : {};

    return {
      name: inputName.value,
      age: parseInt(inputAge.value, 10),
      horizon_years: parseInt(inputHorizon.value, 10),
      monthly_income: parseFloat(inputIncome.value),
      monthly_expenses: parseFloat(inputExpenses.value),
      current_emergency_reserve: parseFloat(inputEmergency.value),
      income_stability_score: parseInt(inputStability.value, 10),
      loss_tolerance_score: parseInt(inputLossTolerance.value, 10),
      goals: existingGoals,
      current_portfolio: existingPortfolio
    };
  }

  // Dashboard Renderer
  function renderDashboard(data) {
    renderKPIs(data);
    renderGoalsList(data.profile.goals || []);
    renderEmergencyAndCashFlow(data);
    renderHoldingsTable(data);
    renderTargetAllocation(data);
    renderGoalsTable(data.goal_plan);
    renderPortfolioHealth(data);
    renderMonteCarlo(data.simulation);
    renderMarketRegimeAndInsights(data);
  }

  // 1. KPI Top Bar
  function renderKPIs(data) {
    const health = data.portfolio_analytics.health_score || 0;
    document.getElementById("kpiHealthScore").textContent = health;
    document.getElementById("barHealthScore").style.width = `${health}%`;
    document.getElementById("kpiHealthDesc").textContent = getHealthDescription(health);

    const cf = data.cash_flow;
    document.getElementById("kpiSurplus").textContent = formatINR(cf.investable_surplus);
    document.getElementById("kpiSavingsRate").textContent = `Savings Rate: ${cf.savings_rate_pct}%`;
    document.getElementById("kpiIncomeExpenseSub").textContent = `Income: ${formatINR(cf.monthly_income)} | Expenses: ${formatINR(cf.monthly_expenses)}`;

    const em = data.emergency_fund;
    document.getElementById("kpiEmergencyStatus").textContent = em.status;
    document.getElementById("kpiEmergencyStatus").className = `badge badge-${em.status.includes('Optimal') ? 'emerald' : 'amber'}`;
    document.getElementById("barEmergency").style.width = `${em.readiness_pct}%`;
    document.getElementById("kpiEmergencySub").textContent = `${em.months_covered} Months covered of ${em.target_months} Recommended`;

    const rp = data.risk_profile;
    document.getElementById("kpiRiskPosture").textContent = rp.posture;
    document.getElementById("kpiRiskScoreBadge").textContent = `Risk Score: ${rp.risk_score} / 100`;
    document.getElementById("kpiRiskHorizonSub").textContent = `Target Horizon: ${data.profile.horizon_years} Years`;
  }

  function getHealthDescription(score) {
    if (score >= 80) return "Optimal Asset Mix & Low Vulnerability";
    if (score >= 60) return "Good Alignment — Minor Adjustments Advised";
    if (score >= 40) return "Moderate Risk — Action Plan Recommended";
    return "Needs Rebalancing to Protect Capital";
  }

  // 2. Goals List
  function renderGoalsList(goals) {
    goalsListContainer.innerHTML = "";
    if (!goals || goals.length === 0) {
      goalsListContainer.innerHTML = `<p style="font-size:0.8rem; color:var(--text-subtle);">No financial goals configured yet.</p>`;
      return;
    }

    goals.forEach((g) => {
      const card = document.createElement("div");
      card.className = "opportunity-card";
      card.style.padding = "14px";
      card.style.background = "rgba(15, 23, 42, 0.6)";
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h5 style="font-size:0.95rem; font-weight:700;">${g.name}</h5>
            <span style="font-size:0.8rem; color:var(--text-muted);">${formatCompactINR(g.target_amount)} in ${g.timeline_years} yrs (${g.expected_return_pct}% return)</span>
          </div>
          <button type="button" class="btn-delete-goal" data-id="${g.id}" style="background:transparent; border:none; color:var(--accent-rose); cursor:pointer;">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      `;

      card.querySelector(".btn-delete-goal").addEventListener("click", (e) => {
        const goalId = e.currentTarget.getAttribute("data-id");
        currentProfileData.profile.goals = currentProfileData.profile.goals.filter((item) => item.id !== goalId);
        recalculatePlan();
      });

      goalsListContainer.appendChild(card);
    });
  }

  // 3. Emergency & Cash Flow
  function renderEmergencyAndCashFlow(data) {
    const em = data.emergency_fund;
    document.getElementById("emTargetReserve").textContent = formatINR(em.target_reserve);
    document.getElementById("emCurrentReserve").textContent = formatINR(em.current_reserve);
    document.getElementById("emGap").textContent = formatINR(em.reserve_gap);

    const recText = (em.reserve_gap > 0)
      ? `Allocate approximately ${formatINR(em.reserve_gap)} to liquid bank savings or fixed deposits before committing heavily to long-term equity stocks.`
      : `Your emergency safety reserve is fully funded! Available monthly surplus can be invested directly into target goals.`;
    document.getElementById("emRecommendationText").textContent = recText;
  }

  // 4. Holdings Table in Tab 2
  function renderHoldingsTable(data) {
    const pa = data.portfolio_analytics;
    const targetWeights = data.target_allocation.weights_pct;
    const currentWeights = pa.current_weights_pct;

    const tbody = document.getElementById("holdingsTable").querySelector("tbody");
    tbody.innerHTML = "";

    const assetRows = [
      { name: "Domestic Equity (Indian Stocks)", key: "equity_domestic", desc: "Long-term growth in Indian corporate sector" },
      { name: "Debt & Fixed Income (FDs / Bonds)", key: "debt", desc: "Guaranteed interest & principal safety" },
      { name: "Gold & Precious Metals", key: "gold", desc: "Inflation protection & market crash buffer" },
      { name: "Liquid Cash / Savings", key: "cash", desc: "Instant emergency liquidity" },
      { name: "International Equity (Global)", key: "equity_international", desc: "US Tech & global geographical exposure" }
    ];

    assetRows.forEach((asset) => {
      const cur = currentWeights[asset.key] || 0;
      const tgt = targetWeights[asset.key] || 0;
      const diff = cur - tgt;

      let badgeClass = "badge-info";
      let actionText = "Maintain";
      if (diff < -3) {
        badgeClass = "badge-emerald";
        actionText = "Keep Buying / Accumulate";
      } else if (diff > 3) {
        badgeClass = "badge-amber";
        actionText = "Slight Overweight — Rebalance";
      }

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>
          <strong>${asset.name}</strong>
          <div style="font-size:0.75rem; color:var(--text-subtle);">${asset.desc}</div>
        </td>
        <td>${cur.toFixed(1)}%</td>
        <td class="font-bold text-cyan">${tgt.toFixed(1)}%</td>
        <td><span class="badge ${badgeClass}">${actionText}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  // 5. Target Asset Allocation
  function renderTargetAllocation(data) {
    const alloc = data.target_allocation;
    const weights = alloc.weights_pct;
    const splits = alloc.monthly_split_inr;

    renderChart("assetAllocationChart", {
      type: "doughnut",
      data: {
        labels: ["Domestic Equity", "Debt", "Gold", "Cash/Liquid", "Int'l Equity"],
        datasets: [{
          data: [
            weights.equity_domestic,
            weights.debt,
            weights.gold,
            weights.cash,
            weights.equity_international
          ],
          backgroundColor: ["#06b6d4", "#6366f1", "#f59e0b", "#10b981", "#a855f7"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom", labels: { color: "#9ca3af" } } },
        cutout: "65%"
      }
    });

    const tbody = document.getElementById("assetSplitTable").querySelector("tbody");
    tbody.innerHTML = `
      <tr><td><i class="fa-solid fa-square text-cyan"></i> Domestic Equity</td><td>${weights.equity_domestic}%</td><td class="text-cyan font-bold">${formatINR(splits.equity_domestic)}</td></tr>
      <tr><td><i class="fa-solid fa-square text-indigo"></i> Debt & Fixed Income</td><td>${weights.debt}%</td><td class="text-indigo font-bold">${formatINR(splits.debt)}</td></tr>
      <tr><td><i class="fa-solid fa-square text-amber"></i> Gold & Metals</td><td>${weights.gold}%</td><td class="text-amber font-bold">${formatINR(splits.gold)}</td></tr>
      <tr><td><i class="fa-solid fa-square text-emerald"></i> Liquid / Cash</td><td>${weights.cash}%</td><td class="text-emerald font-bold">${formatINR(splits.cash)}</td></tr>
      <tr><td><i class="fa-solid fa-square text-purple"></i> International Equity</td><td>${weights.equity_international}%</td><td class="text-purple font-bold">${formatINR(splits.equity_international)}</td></tr>
    `;
  }

  // 6. Goals Table
  function renderGoalsTable(goalPlan) {
    const tbody = document.getElementById("goalsTable").querySelector("tbody");
    tbody.innerHTML = "";

    const feasBadge = document.getElementById("goalFeasibilityBadge");
    feasBadge.textContent = goalPlan.feasibility;
    feasBadge.className = `badge badge-${goalPlan.feasibility_badge}`;

    document.getElementById("totalReqSipVal").textContent = formatINR(goalPlan.total_required_sip);
    
    const bufText = (goalPlan.surplus_gap_or_buffer >= 0)
      ? `Surplus Buffer: ${formatINR(goalPlan.surplus_gap_or_buffer)}`
      : `Surplus Deficit: ${formatINR(Math.abs(goalPlan.surplus_gap_or_buffer))}`;
    document.getElementById("surplusGapCell").textContent = bufText;

    if (!goalPlan.goals || goalPlan.goals.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-subtle);">No financial goals configured yet. Click 'Add Goal' in Tab 1.</td></tr>`;
      return;
    }

    goalPlan.goals.forEach((g) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${g.name}</strong></td>
        <td>${formatCompactINR(g.target_amount)}</td>
        <td>${g.timeline_years} Yrs</td>
        <td>${g.expected_return_pct}%</td>
        <td class="text-amber font-bold">${formatINR(g.required_monthly_sip)}</td>
        <td><span class="badge badge-info">${g.priority}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  // 7. Portfolio Health & Comparison
  function renderPortfolioHealth(data) {
    const pa = data.portfolio_analytics;
    const targetWeights = data.target_allocation.weights_pct;
    const currentWeights = pa.current_weights_pct;

    document.getElementById("valAlignmentScore").textContent = `${pa.alignment_score}%`;
    document.getElementById("valDiversificationScore").textContent = `${pa.diversification_score} / 100`;
    document.getElementById("valPortfolioTotal").textContent = formatCompactINR(pa.total_value);

    renderChart("portfolioComparisonChart", {
      type: "bar",
      data: {
        labels: ["Dom Equity", "Debt", "Gold", "Cash", "Int'l Equity"],
        datasets: [
          { label: "Current %", data: [currentWeights.equity_domestic||0, currentWeights.debt||0, currentWeights.gold||0, currentWeights.cash||0, currentWeights.equity_international||0], backgroundColor: "#6366f1" },
          { label: "Target %", data: [targetWeights.equity_domestic||0, targetWeights.debt||0, targetWeights.gold||0, targetWeights.cash||0, targetWeights.equity_international||0], backgroundColor: "#06b6d4" }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "top", labels: { color: "#9ca3af" } } },
        scales: {
          x: { ticks: { color: "#9ca3af" }, grid: { display: false } },
          y: { ticks: { color: "#9ca3af" }, grid: { color: "rgba(255,255,255,0.05)" } }
        }
      }
    });

    const sectors = pa.sector_breakdown || [];
    const secLabels = sectors.map((s) => s.sector);
    const secData = sectors.map((s) => s.weight_pct);

    renderChart("sectorChart", {
      type: "bar",
      data: {
        labels: secLabels.length ? secLabels : ["No Specific Sector Overweight"],
        datasets: [{
          label: "Sector Weight %",
          data: secData.length ? secData : [100],
          backgroundColor: "#10b981"
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#9ca3af" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: { ticks: { color: "#9ca3af" }, grid: { display: false } }
        }
      }
    });

    const rebalanceList = document.getElementById("rebalanceList");
    rebalanceList.innerHTML = "";
    (pa.rebalancing_suggestions || []).forEach((sug) => {
      const li = document.createElement("li");
      li.textContent = sug;
      rebalanceList.appendChild(li);
    });
  }

  // 8. Monte Carlo Simulation Chart
  function renderMonteCarlo(sim) {
    const outcomes = sim.outcomes;
    document.getElementById("valP10").textContent = formatCompactINR(outcomes.conservative_p10);
    document.getElementById("valP50").textContent = formatCompactINR(outcomes.base_p50);
    document.getElementById("valP90").textContent = formatCompactINR(outcomes.optimistic_p90);

    const ts = sim.time_series || [];
    const labels = ts.map((item) => `Yr ${item.year}`);
    const p10Data = ts.map((item) => item.conservative_p10);
    const p50Data = ts.map((item) => item.base_p50);
    const p90Data = ts.map((item) => item.optimistic_p90);

    renderChart("monteCarloChart", {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          { label: "Optimistic Scenario (90th %ile)", data: p90Data, borderColor: "#10b981", backgroundColor: "rgba(16, 185, 129, 0.1)", fill: true, tension: 0.3 },
          { label: "Expected Base Case (50th %ile)", data: p50Data, borderColor: "#06b6d4", backgroundColor: "transparent", borderWidth: 3, tension: 0.3 },
          { label: "Conservative Market (10th %ile)", data: p10Data, borderColor: "#f59e0b", backgroundColor: "rgba(245, 158, 11, 0.1)", fill: true, tension: 0.3 }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "top", labels: { color: "#9ca3af" } },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.dataset.label}: ${formatCompactINR(context.raw)}`;
              }
            }
          }
        },
        scales: {
          x: { ticks: { color: "#9ca3af" }, grid: { color: "rgba(255,255,255,0.05)" } },
          y: {
            ticks: {
              color: "#9ca3af",
              callback: function (val) { return formatCompactINR(val); }
            },
            grid: { color: "rgba(255,255,255,0.05)" }
          }
        }
      }
    });
  }

  // 9. Market Context & Insights
  function renderMarketRegimeAndInsights(data) {
    const regime = data.market_regime;
    document.getElementById("marketRegimeTitle").textContent = regime.regime;
    document.getElementById("marketRegimeBias").textContent = `Tactical Bias: ${regime.tactical_bias}`;

    const ul = document.getElementById("plainLanguageInsights");
    ul.innerHTML = "";
    (data.insights || []).forEach((ins) => {
      const li = document.createElement("li");
      li.textContent = ins;
      ul.appendChild(li);
    });
  }

  // Chart Helper
  function renderChart(canvasId, config) {
    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
    }
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    chartInstances[canvasId] = new Chart(ctx, config);
  }

  // Run initialization
  init();
});
