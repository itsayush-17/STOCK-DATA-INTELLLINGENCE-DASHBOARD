# Smart Investment & Portfolio Analytics

An India-focused investment decision-support platform that analyzes a user's income, expenses, risk tolerance, financial goals, current portfolio, and market conditions to generate data-driven allocation guidance and scenario planning.

> **Disclaimer**: This repository is positioned as an educational analytics tool, not a source of guaranteed financial advice. Returns and risk estimates are model-driven assumptions, not guarantees. Historical patterns and simulated outcomes do not ensure future performance. Users should validate important financial decisions with licensed professionals.

---

## Key Features

- **Personalized Investment Planning**: Analyzes income, expenses, financial goals, and risk posture.
- **Emergency-Fund Readiness Checks**: Verifies safety-net coverage before recommending aggressive allocations.
- **Goal-Based SIP Planning**: Calculates required monthly SIPs for major life events and retirement.
- **Portfolio Analytics & Diagnostics**: Evaluates diversification, sector concentration, target alignment, and health scoring.
- **Monte Carlo Scenario Simulation**: Runs 1,000-path stochastic simulations for conservative (10th percentile), base (50th percentile), and optimistic (90th percentile) outcomes.
- **India-Focused Market & Macro Dashboard**: Tracks Indian indices (NIFTY 50, SENSEX, Midcaps), global context, RBI repo rate, CPI inflation, yield curves, and USD/INR rates.
- **Plain-Language Explanation Layer**: Translates quantitative metrics into clear, actionable executive takeaways.

---

## System Architecture

```text
Market + Macro Inputs
        |
        v
Seeded Data / Future ETL Layer
        |
        v
Analytics Engine
  - cash flow
  - emergency fund
  - risk score
  - allocation model
  - portfolio review
  - goal planning
  - simulation
        |
        v
Local API Server
        |
        v
Interactive Dashboard
```

---

## Project Structure

```text
backend/
  analytics/
    __init__.py
    engine.py
    seed.py
  server.py
  tests_smoke.py
frontend/
  app.js
  index.html
  styles.css
.github/
  ISSUE_TEMPLATE/
    bug_report.md
  workflows/
    ci.yml
CODE_OF_CONDUCT.md
CONTRIBUTING.md
LICENSE
README.md
SECURITY.md
requirements.txt
requirements-dev.txt
```

---

## Quickstart & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/itsayush-17/smart-investment-portfolio-analytics.git
   cd smart-investment-portfolio-analytics
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Launch local server**:
   ```bash
   python backend/server.py
   ```

5. **Open Dashboard**:
   Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.

6. **Run Smoke Tests**:
   ```bash
   pytest backend/tests_smoke.py
   ```

---

## API Endpoints

- `GET /api/bootstrap` - Returns the seeded analysis payload, user profile, and market snapshot for initial page load.
- `GET /api/analyze` - Returns the default analysis payload.
- `POST /api/analyze` - Accepts a partial or full user profile payload and recalculates all analytics responses in real time.

---

## Future Roadmap

- Replace seeded market data with scheduled ingestion from trusted live market APIs
- Upgrade the server layer to FastAPI
- Persist users, goals, and transactions in PostgreSQL
- Add authentication and multi-user support
- Add downloadable PDF reports and richer interactive visualizations
- Introduce historical portfolio tracking and rebalancing alerts

---

## Contributing & License

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.  
This project is licensed under the [MIT License](LICENSE).
