from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import certifi
import numpy as np
import pandas as pd

# Some Anaconda builds expose `certifi` without a `where()` helper, while
# `yfinance` requires it through `curl_cffi`.
if not hasattr(certifi, "where"):
    certifi_path = next(iter(certifi.__path__), None)
    certifi.where = lambda: str(Path(certifi_path) / "cacert.pem") if certifi_path else ""

try:
    import yfinance as yf
except ImportError:  # pragma: no cover - handled at runtime
    yf = None


SUPPORTED_COMPANIES = {
    "INFY": {"name": "Infosys Ltd.", "ticker": "INFY.NS"},
    "TCS": {"name": "Tata Consultancy Services", "ticker": "TCS.NS"},
    "RELIANCE": {"name": "Reliance Industries Ltd.", "ticker": "RELIANCE.NS"},
}


class StockDataError(Exception):
    pass


@dataclass
class StockDataService:
    history_period: str = "18mo"

    def _resolve_company(self, symbol: str) -> dict[str, str]:
        company = SUPPORTED_COMPANIES.get(symbol.upper())
        if not company:
            raise StockDataError(f"Unsupported symbol '{symbol}'.")
        return company

    def _load_history(self, symbol: str) -> pd.DataFrame:
        if yf is None:
            raise RuntimeError(
                "yfinance is not installed. Run `pip install -r requirements.txt`."
            )

        ticker = self._resolve_company(symbol)["ticker"]
        frame = yf.download(
            ticker,
            period=self.history_period,
            interval="1d",
            progress=False,
            auto_adjust=False,
        )

        if frame.empty:
            raise StockDataError(f"No market data available for '{symbol.upper()}'.")

        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = [column[0] for column in frame.columns.to_flat_index()]

        frame = frame.reset_index()
        date_column = "Date" if "Date" in frame.columns else frame.columns[0]
        frame[date_column] = pd.to_datetime(frame[date_column]).dt.tz_localize(None)
        frame = frame.rename(columns={date_column: "Date"})

        columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        frame = frame[columns].copy()
        frame = frame.dropna(subset=["Open", "High", "Low", "Close"]).sort_values("Date")
        frame["daily_return_pct"] = ((frame["Close"] - frame["Open"]) / frame["Open"]) * 100
        frame["ma7"] = frame["Close"].rolling(7).mean()
        frame["ma20"] = frame["Close"].rolling(20).mean()
        frame["date"] = frame["Date"].dt.strftime("%Y-%m-%d")
        return frame

    def _get_52_week_frame(self, symbol: str) -> pd.DataFrame:
        frame = self._load_history(symbol).copy()
        latest_date = frame["Date"].max()
        cutoff = latest_date - pd.Timedelta(days=365)
        year_frame = frame[frame["Date"] >= cutoff].copy()

        if year_frame.empty:
            raise StockDataError(f"Not enough 52-week data available for '{symbol.upper()}'.")

        return year_frame

    def get_stock_data(self, symbol: str, days: int = 30) -> dict:
        company = self._resolve_company(symbol)
        frame = self._load_history(symbol).tail(days).copy()

        records = []
        for row in frame.to_dict(orient="records"):
            records.append(
                {
                    "date": row["date"],
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                    "daily_return_pct": round(float(row["daily_return_pct"]), 2),
                    "ma7": None if pd.isna(row["ma7"]) else round(float(row["ma7"]), 2),
                    "ma20": None if pd.isna(row["ma20"]) else round(float(row["ma20"]), 2),
                }
            )

        return {
            "symbol": symbol.upper(),
            "name": company["name"],
            "days": days,
            "records": records,
        }

    def get_summary(self, symbol: str) -> dict:
        company = self._resolve_company(symbol)
        frame = self._get_52_week_frame(symbol)

        if len(frame) < 2:
            raise StockDataError(f"Not enough data available for '{symbol.upper()}'.")

        latest = frame.iloc[-1]
        previous = frame.iloc[-2]
        change = float(latest["Close"] - previous["Close"])
        change_pct = (change / float(previous["Close"])) * 100 if previous["Close"] else 0.0

        return {
            "symbol": symbol.upper(),
            "name": company["name"],
            "period": "52-week",
            "current_price": round(float(latest["Close"]), 2),
            "price_change": round(change, 2),
            "price_change_pct": round(change_pct, 2),
            "week_52_high": round(float(frame["High"].max()), 2),
            "week_52_low": round(float(frame["Low"].min()), 2),
            "average_close": round(float(frame["Close"].mean()), 2),
            "average_volume": int(frame["Volume"].mean()),
            "volatility_score": round(float(frame["daily_return_pct"].std(ddof=0)), 2),
            "latest_ma7": round(float(latest["ma7"]), 2) if pd.notna(latest["ma7"]) else None,
            "latest_ma20": round(float(latest["ma20"]), 2) if pd.notna(latest["ma20"]) else None,
            "last_updated": latest["date"],
        }

    def get_forecast(self, symbol: str, days: int = 30, future_days: int = 7) -> dict:
        company = self._resolve_company(symbol)
        frame = self._load_history(symbol).tail(days).copy()

        if len(frame) < 5:
            raise StockDataError(
                f"Not enough data available to build a forecast for '{symbol.upper()}'."
            )

        closes = frame["Close"].astype(float).to_numpy()
        x_values = np.arange(len(closes))
        slope, intercept = np.polyfit(x_values, closes, 1)

        future_x = np.arange(len(closes), len(closes) + future_days)
        predictions = intercept + slope * future_x

        last_date = frame["Date"].iloc[-1]
        future_dates = pd.bdate_range(
            start=last_date + pd.offsets.BDay(1), periods=future_days
        )

        latest_close = float(closes[-1])
        projected_close = float(predictions[-1])
        projected_change_pct = (
            ((projected_close - latest_close) / latest_close) * 100 if latest_close else 0.0
        )

        return {
            "symbol": symbol.upper(),
            "name": company["name"],
            "days_used": days,
            "future_days": future_days,
            "method": "Linear trend projection based on recent closing prices.",
            "history": [
                {
                    "date": row["date"],
                    "close": round(float(row["Close"]), 2),
                }
                for row in frame.to_dict(orient="records")
            ],
            "forecast": [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "close": round(float(value), 2),
                }
                for date, value in zip(future_dates, predictions)
            ],
            "latest_close": round(latest_close, 2),
            "projected_close": round(projected_close, 2),
            "projected_change_pct": round(projected_change_pct, 2),
            "trend": "Bullish" if projected_change_pct >= 0 else "Bearish",
        }

    def compare_stocks(self, symbol1: str, symbol2: str, days: int = 30) -> dict:
        if symbol1.upper() == symbol2.upper():
            raise ValueError("Choose two different symbols to compare.")

        frame1 = self._load_history(symbol1).tail(days).copy()
        frame2 = self._load_history(symbol2).tail(days).copy()

        frame1["normalized"] = (frame1["Close"] / frame1["Close"].iloc[0]) * 100
        frame2["normalized"] = (frame2["Close"] / frame2["Close"].iloc[0]) * 100

        merged = pd.merge(
            frame1[["date", "normalized"]],
            frame2[["date", "normalized"]],
            on="date",
            how="inner",
            suffixes=(f"_{symbol1.upper()}", f"_{symbol2.upper()}"),
        )

        return {
            "symbol1": symbol1.upper(),
            "symbol2": symbol2.upper(),
            "days": days,
            "dates": merged["date"].tolist(),
            "series": [
                {
                    "symbol": symbol1.upper(),
                    "values": [
                        round(float(value), 2)
                        for value in merged[f"normalized_{symbol1.upper()}"]
                    ],
                },
                {
                    "symbol": symbol2.upper(),
                    "values": [
                        round(float(value), 2)
                        for value in merged[f"normalized_{symbol2.upper()}"]
                    ],
                },
            ],
        }
