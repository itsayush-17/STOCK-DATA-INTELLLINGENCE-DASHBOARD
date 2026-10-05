"""Simple local API and static file server for the investment analytics platform."""

from __future__ import annotations

import json
import mimetypes
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from analytics.engine import bootstrap_payload, build_analysis

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
MAX_REQUEST_BYTES = 64 * 1024


class InvestmentRequestHandler(SimpleHTTPRequestHandler):
    """Serve API responses and the static frontend from one process."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self) -> None:
        """Attach lightweight browser-safety headers to every response."""
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def _send_not_found(self) -> None:
        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def _read_json_body(self) -> dict:
        """Read a small JSON object and reject malformed client input."""
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Content-Length must be a valid integer.") from error

        if content_length < 0 or content_length > MAX_REQUEST_BYTES:
            raise ValueError("Request body must be smaller than 64 KB.")

        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Request body must contain valid JSON.") from error

        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        return payload

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/bootstrap":
            self._send_json(bootstrap_payload())
            return
        if parsed.path == "/api/analyze":
            self._send_json(build_analysis())
            return
        if parsed.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/analyze":
            self._send_not_found()
            return

        try:
            payload = self._read_json_body()
            analysis = build_analysis(payload)
        except (KeyError, TypeError, ValueError) as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(analysis)

    def guess_type(self, path: str) -> str:
        if path.endswith(".js"):
            return "application/javascript; charset=utf-8"
        guessed = mimetypes.guess_type(path)[0]
        return guessed or "application/octet-stream"


def run() -> None:
    """Start the local development server."""
    server = ThreadingHTTPServer((HOST, PORT), InvestmentRequestHandler)
    print(f"Northstar investment learning site running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
