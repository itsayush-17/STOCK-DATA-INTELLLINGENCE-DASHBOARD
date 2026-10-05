# Northstar — Smart Investment & Portfolio Analytics

[![CI](https://github.com/itsayush-17/STOCK-DATA-INTELLLINGENCE-DASHBOARD/actions/workflows/ci.yml/badge.svg)](https://github.com/itsayush-17/STOCK-DATA-INTELLLINGENCE-DASHBOARD/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-0b7285.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-1f6feb.svg)](https://www.python.org/)

Northstar is an India-focused learning and analytics site for people who want to understand their money before making investment decisions. It brings cash-flow planning, risk education, portfolio concepts, market context, and simple explanations into one place.

The project is educational. It is not SEBI-registered investment advice, does not execute trades, and never promises returns.

## What is in this repository

### Website

- Separate Overview, Markets, Portfolio, Planning, and Learn pages
- Responsive layout with light and dark themes
- Example cash-flow, risk, goal, and portfolio summaries
- Beginner-friendly explanations and a visible education disclaimer
- Clear sample-data labels: current market and portfolio figures are bundled demonstrations, not live prices or personal account data

### Analytics and API foundation

- Cash-flow and emergency-fund calculations
- Risk-profile exercise and illustrative asset mix
- Goal, SIP, lump-sum, and scenario calculators
- FastAPI routes for registration, sign-in, investment guides, private holdings, and planning tools
- SQLAlchemy models and an Alembic migration; SQLite by default, PostgreSQL supported through `DATABASE_URL`
- Seed library with 19 beginner-oriented India and international investment guides

## Current data limits

The visible website uses sample market and portfolio information. It does not yet fetch live market prices or connect the website portfolio screen to user accounts. The FastAPI service is a separate API foundation at this stage. Guide text about returns, taxes, rates, and regulations is educational starter content and must be checked against current official information before publication.

## Project structure

```text
backend/
  analytics/             Existing planning and analytics engine
  api/                   FastAPI routes, models, schemas, guide seed, and auth
  migrations/             Alembic migration environment and revisions
  server.py               Website and legacy analytics API server
  tests_smoke.py          Analytics smoke tests
frontend/
  index.html              Multi-page single-document website
  styles.css              Responsive visual system and themes
  app.js                  Navigation, rendering, and planner interactions
alembic.ini
Dockerfile
requirements.txt
requirements-dev.txt
README.md
```

## Run locally on Windows

Clone the repository, then run commands from its folder in PowerShell:

```powershell
git clone https://github.com/itsayush-17/STOCK-DATA-INTELLLINGENCE-DASHBOARD.git
Set-Location .\STOCK-DATA-INTELLLINGENCE-DASHBOARD
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe backend\server.py
```

Open <http://127.0.0.1:8000>. Keep that PowerShell window open while using the site.

### Start the FastAPI service

In a second PowerShell window, from the same repository folder:

```powershell
Set-Location .\STOCK-DATA-INTELLLINGENCE-DASHBOARD
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn backend.api.main:app --reload --port 8001
```

The API docs are at <http://127.0.0.1:8001/docs>. SQLite is the default database. To use PostgreSQL, set `DATABASE_URL` to a SQLAlchemy URL such as `postgresql+psycopg://user:password@localhost:5432/investments` before running the migration. Set a private random `JWT_SECRET` before deployment. Production mode refuses to start without it.

## API routes

| Route | Access | Purpose |
| --- | --- | --- |
| `GET /api/v1/health` | Public | Service status and education disclaimer |
| `POST /api/v1/auth/register` | Public | Create an account |
| `POST /api/v1/auth/login` | Public | Sign in and receive a bearer token |
| `GET /api/v1/auth/me` | Signed in | Return the current account |
| `GET /api/v1/guides` | Public | Search guides by name, region, or category |
| `GET /api/v1/guides/{slug}` | Public | Read one investment guide |
| `/api/v1/portfolio/holdings` | Signed in | List, add, edit, or remove holdings |
| `GET /api/v1/portfolio/summary` | Signed in | Summarize recorded holdings and concentration |
| `POST /api/v1/tools/risk-profile` | Public | Run the sample risk exercise |
| `POST /api/v1/tools/emergency-fund` | Public | Estimate an emergency reserve gap |
| `POST /api/v1/tools/sip-calculator` | Public | Estimate regular contributions under an assumption |
| `POST /api/v1/tools/lumpsum-calculator` | Public | Estimate a one-time investment under an assumption |
| `POST /api/v1/tools/goal-planner` | Public | Estimate monthly savings toward a goal |
| `POST /api/v1/tools/monte-carlo` | Public | Show illustrative 10th, 50th, and 90th percentile scenarios |
| `GET /api/v1/tools/compare?slugs=ppf,index-mutual-fund` | Public | Compare two or three guide entries |

Signed-in routes use `Authorization: Bearer <access_token>`. Interactive API documentation at `/docs` shows request and response schemas.

Example account request:

```json
{
  "email": "learner@example.com",
  "password": "use-a-long-unique-password"
}
```

Example holding request:

```json
{
  "asset_type": "Mutual fund",
  "name": "Broad market index fund",
  "category": "Equity",
  "sector": "Diversified",
  "country": "India",
  "quantity": 10,
  "invested_amount": 5000,
  "current_value": 5200,
  "buy_price": 500,
  "buy_date": "2025-01-15",
  "platform": "My broker"
}
```

## Docker

The current Docker image runs the sample website and its legacy analytics endpoints:

```powershell
docker build -t northstar-investment-analytics .
docker run --rm -p 8000:8000 northstar-investment-analytics
```

Open <http://127.0.0.1:8000>. The FastAPI database service is not yet wired into this single-container website deployment.

## Development checks

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests_smoke.py
.\.venv\Scripts\python.exe -m ruff check backend
```

GitHub Actions runs the Python smoke tests and Ruff checks on pushes and pull requests to `main`.

## Architecture

```text
Sample market/profile inputs ──> Analytics engine ──> Website server ──> Browser pages
                                      │
                                      └──> FastAPI API ──> SQLAlchemy ──> SQLite / PostgreSQL
```

## Screenshots

Add current Overview, Markets, Portfolio, Planning, and Learn screenshots here as those pages are reviewed.

## Roadmap

- Connect the website pages to the authenticated portfolio API
- Add a reviewed market-data provider, cache, refresh schedule, and last-known-data fallback
- Expand the investment explorer and learning library
- Add richer historical portfolio charts, imports, and downloadable reports
- Complete deployment configuration and end-to-end checks

## Responsible use

- This site is for education and planning practice, not personalized investment advice.
- Returns are not guaranteed. Historical performance and scenarios do not predict future results.
- Higher-risk assets can lose substantial value; review risks, fees, liquidity, taxes, and current rules.
- Consider a licensed financial or tax professional for decisions specific to you.

## License

MIT. See [LICENSE](./LICENSE).
