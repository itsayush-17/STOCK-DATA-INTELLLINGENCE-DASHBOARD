# Stock Intelligence Dashboard

A mini stock market analytics system built with Flask, Pandas, NumPy, SQLite, and yfinance. The project fetches live NSE stock data, computes useful market indicators, stores cached history in SQLite, exposes backend APIs, and presents the results in a clean dashboard.

This is designed as a strong assignment submission: simple enough to finish reliably, but polished enough to demonstrate backend, data-processing, API design, and frontend integration skills.

## What This Project Shows

- Python backend development with Flask
- Data handling and transformation with Pandas
- Analytical calculations like moving averages, volatility, and returns
- Local persistence with SQLite caching
- REST API design for dashboards
- Frontend integration with Chart.js
- Basic deployment readiness with Gunicorn, Docker, and Render config

## Core Features

- Left-side clickable company list for `INFY`, `TCS`, and `RELIANCE`
- Historical stock data view for 30, 60, or 90 days
- Summary cards for current price, 52-week high/low, average close, volatility, and daily change
- 7-day and 20-day moving average visualization
- Stock comparison chart using normalized performance
- Short-term 7-business-day forecast using a simple linear trend projection
- Health endpoint and production entrypoint for deployment

## Tech Stack

- Backend: Flask
- Data: Pandas, NumPy, SQLite
- Market data source: yfinance
- Frontend: HTML, CSS, JavaScript, Chart.js
- Deployment: Gunicorn, Docker, Render

## Architecture

```text
Yahoo Finance
     |
     v
StockDataService
     |
     +--> data cleaning
     +--> returns
     +--> moving averages
     +--> volatility
     +--> forecast projection
     +--> SQLite cache
     |
     v
Flask API
     |
     +--> /companies
     +--> /data/<symbol>
     +--> /summary/<symbol>
     +--> /api/forecast/<symbol>
     +--> /compare
     |
     v
Dashboard UI
```

## Project Structure

```text
.
|-- app.py
|-- database.py
|-- wsgi.py
|-- requirements.txt
|-- Procfile
|-- render.yaml
|-- Dockerfile
|-- postman/
|   `-- Stock-Intelligence-Dashboard.postman_collection.json
|-- services/
|   `-- stock_service.py
|-- static/
|   |-- app.js
|   `-- style.css
`-- templates/
    `-- index.html
```

## Local Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python app.py
   ```

4. Open:

   ```text
   http://127.0.0.1:5000
   ```

If your default Python setup is unstable, this workspace also includes a verified environment:

```bash
.venv314\Scripts\activate
python app.py
```

## API Endpoints

- `GET /companies`
- `GET /data/<symbol>?days=30`
- `GET /summary/<symbol>`
- `GET /compare?symbol1=INFY&symbol2=TCS&days=30`
- `GET /api/forecast/<symbol>?days=30&future_days=7`
- `GET /health`

### Example Response: `/summary/INFY`

```json
{
  "symbol": "INFY",
  "name": "Infosys Ltd.",
  "period": "52-week",
  "current_price": 1524.8,
  "price_change": 18.45,
  "price_change_pct": 1.22,
  "week_52_high": 1588.3,
  "week_52_low": 1451.2,
  "average_close": 1512.9,
  "volatility_score": 1.84,
  "last_updated": "2026-03-30"
}
```

### Example Response: `/api/forecast/INFY?days=30&future_days=7`

```json
{
  "symbol": "INFY",
  "future_days": 7,
  "method": "Linear trend projection based on recent closing prices.",
  "latest_close": 1524.8,
  "projected_close": 1541.3,
  "projected_change_pct": 1.08,
  "trend": "Bullish"
}
```

## Deployment

This repo is ready for basic deployment:

- `wsgi.py` exposes the Flask app for Gunicorn
- `Procfile` works for platforms like Render or Railway
- `render.yaml` helps bootstrap a Render web service
- `Dockerfile` supports container deployment
- `postman/Stock-Intelligence-Dashboard.postman_collection.json` is included for API testing
- `stock_dashboard.db` is created automatically as the local SQLite cache when the app runs

Production command:

```bash
gunicorn wsgi:app
```

## Why This Stands Out In A Submission

- It covers the full stack instead of stopping at data analysis
- The APIs are structured cleanly and are easy to test
- The dashboard is simple, readable, and actually useful
- The compare view and forecast feature add bonus value without overcomplicating the project
- The repository includes deployment support, which makes the project feel more complete

## Important Notes

- Supported symbols are currently limited to `INFY`, `TCS`, and `RELIANCE`
- `days` must be between `5` and `365`
- `future_days` must be between `3` and `30`
- The forecast is a lightweight trend projection for demonstration purposes, not financial advice
- SQLite is used as a local persistence layer for cached stock history
- On this machine, the project was verified successfully with `.venv314\Scripts\python.exe`

## Possible Future Improvements

- Add more NSE companies dynamically
- Cache API responses to reduce repeated Yahoo Finance calls
- Add candlestick charts
- Add export-to-CSV support
- Replace the simple forecast with a stronger time-series model
