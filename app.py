import os

from flask import Flask, jsonify, render_template, request

from services.stock_service import (
    StockDataError,
    StockDataService,
    SUPPORTED_COMPANIES,
)

def create_app() -> Flask:
    app = Flask(__name__)
    stock_service = StockDataService()

    def _parse_days(default: int = 30) -> int:
        value = request.args.get("days", default)
        days = int(value)
        if days < 5 or days > 180:
            raise ValueError("days must be between 5 and 180")
        return days

    def _parse_future_days(default: int = 7) -> int:
        value = request.args.get("future_days", default)
        future_days = int(value)
        if future_days < 3 or future_days > 30:
            raise ValueError("future_days must be between 3 and 30")
        return future_days

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

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

    @app.route("/api/data/<symbol>")
    def stock_data(symbol: str):
        try:
            days = _parse_days()
            return jsonify(stock_service.get_stock_data(symbol, days))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except StockDataError as exc:
            return jsonify({"error": str(exc)}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/summary/<symbol>")
    def stock_summary(symbol: str):
        try:
            days = _parse_days(90)
            return jsonify(stock_service.get_summary(symbol, days))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except StockDataError as exc:
            return jsonify({"error": str(exc)}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/forecast/<symbol>")
    def stock_forecast(symbol: str):
        try:
            days = _parse_days(30)
            future_days = _parse_future_days(7)
            return jsonify(stock_service.get_forecast(symbol, days, future_days))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except StockDataError as exc:
            return jsonify({"error": str(exc)}), 404
        except RuntimeError as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/api/compare")
    def compare_stocks():
        symbol1 = request.args.get("symbol1", "INFY")
        symbol2 = request.args.get("symbol2", "TCS")

        try:
            days = _parse_days()
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
    app.run(host="0.0.0.0", port=port, debug=True)
