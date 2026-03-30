import os

from flask import Flask, jsonify, render_template, request

from database import init_db
from services.stock_service import (
    StockDataError,
    StockDataService,
    SUPPORTED_COMPANIES,
)

def create_app() -> Flask:
    app = Flask(__name__)
    init_db()
    stock_service = StockDataService()

    def _parse_future_days(default: int = 7) -> int:
        value = request.args.get("future_days", default)
        future_days = int(value)
        if future_days < 3 or future_days > 30:
            raise ValueError("future_days must be between 3 and 30")
        return future_days

    def _parse_data_days(default: int = 30) -> int:
        value = request.args.get("days", default)
        days = int(value)
        if days < 5 or days > 365:
            raise ValueError("days must be between 5 and 365")
        return days

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/companies")
    @app.route("/api/companies")
    def companies():
        return jsonify(
            [
                {
                    "symbol": symbol,
                    "name": details["name"],
                    "ticker": details["ticker"],
                }
                for symbol, details in SUPPORTED_COMPANIES.items()
            ]
        )

    @app.route("/data/<symbol>")
    @app.route("/api/data/<symbol>")
    def stock_data(symbol: str):
        try:
            days = _parse_data_days()
            return jsonify(stock_service.get_stock_data(symbol, days))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except StockDataError as exc:
            return jsonify({"error": str(exc)}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/summary/<symbol>")
    @app.route("/api/summary/<symbol>")
    def stock_summary(symbol: str):
        try:
            return jsonify(stock_service.get_summary(symbol))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except StockDataError as exc:
            return jsonify({"error": str(exc)}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/forecast/<symbol>")
    def stock_forecast(symbol: str):
        try:
            days = _parse_data_days(30)
            future_days = _parse_future_days(7)
            return jsonify(stock_service.get_forecast(symbol, days, future_days))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except StockDataError as exc:
            return jsonify({"error": str(exc)}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/compare")
    @app.route("/api/compare")
    def compare_stocks():
        symbol1 = request.args.get("symbol1", "INFY")
        symbol2 = request.args.get("symbol2", "TCS")

        try:
            days = _parse_data_days()
            return jsonify(stock_service.compare_stocks(symbol1, symbol2, days))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except StockDataError as exc:
            return jsonify({"error": str(exc)}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
