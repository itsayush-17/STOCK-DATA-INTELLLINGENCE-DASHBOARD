from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path(__file__).resolve().parent / "stock_dashboard.db"


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: str | Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stock_prices (
                symbol TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume INTEGER NOT NULL,
                daily_return_pct REAL,
                ma7 REAL,
                ma20 REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, trade_date)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date
            ON stock_prices(symbol, trade_date DESC)
            """
        )


def cache_stock_data(
    symbol: str, frame: pd.DataFrame, db_path: str | Path = DB_PATH
) -> None:
    rows = [
        (
            symbol.upper(),
            row["date"],
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            int(row["Volume"]),
            float(row["daily_return_pct"]),
            None if pd.isna(row["ma7"]) else float(row["ma7"]),
            None if pd.isna(row["ma20"]) else float(row["ma20"]),
        )
        for row in frame.to_dict(orient="records")
    ]

    with get_connection(db_path) as connection:
        connection.executemany(
            """
            INSERT INTO stock_prices (
                symbol,
                trade_date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                daily_return_pct,
                ma7,
                ma20
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, trade_date) DO UPDATE SET
                open_price = excluded.open_price,
                high_price = excluded.high_price,
                low_price = excluded.low_price,
                close_price = excluded.close_price,
                volume = excluded.volume,
                daily_return_pct = excluded.daily_return_pct,
                ma7 = excluded.ma7,
                ma20 = excluded.ma20,
                updated_at = CURRENT_TIMESTAMP
            """,
            rows,
        )


def load_cached_stock_data(
    symbol: str, db_path: str | Path = DB_PATH
) -> pd.DataFrame:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                trade_date,
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                daily_return_pct,
                ma7,
                ma20
            FROM stock_prices
            WHERE symbol = ?
            ORDER BY trade_date
            """,
            (symbol.upper(),),
        ).fetchall()

    if not rows:
        return pd.DataFrame()

    frame = pd.DataFrame([dict(row) for row in rows])
    frame["Date"] = pd.to_datetime(frame["trade_date"])
    frame["date"] = frame["trade_date"]
    frame = frame.rename(
        columns={
            "open_price": "Open",
            "high_price": "High",
            "low_price": "Low",
            "close_price": "Close",
            "volume": "Volume",
        }
    )
    columns = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "daily_return_pct",
        "ma7",
        "ma20",
        "date",
    ]
    return frame[columns].copy()
