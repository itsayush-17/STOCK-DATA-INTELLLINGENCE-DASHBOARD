"""
Built-in Python HTTP Server for Smart Investment & Portfolio Analytics platform.
Serves API endpoints (/api/bootstrap, /api/analyze) and static frontend files.
"""

import http.server
import json
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Ensure root directory and backend directory are in python path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
for _p in (BASE_DIR, BACKEND_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from backend.analytics.engine import run_full_analysis
from backend.analytics.seed import DEFAULT_MARKET_SNAPSHOT, DEFAULT_USER_PROFILE

FRONTEND_DIR = BASE_DIR / "frontend"


class PortfolioAnalyticsHandler(http.server.BaseHTTPRequestHandler):
    """Custom request handler serving REST API and frontend assets."""

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/bootstrap":
            self._handle_json_response(run_full_analysis())
        elif path == "/api/analyze":
            self._handle_json_response(run_full_analysis())
        else:
            self._serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/analyze":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length) if content_length > 0 else b"{}"
                payload = json.loads(body.decode("utf-8")) if body else {}
                response_data = run_full_analysis(payload)
                self._handle_json_response(response_data)
            except Exception as exc:
                self._handle_json_response({"error": f"Failed to calculate analytics: {str(exc)}"}, status=400)
        else:
            self._handle_json_response({"error": "Endpoint not found"}, status=404)

    def _handle_json_response(self, data: dict, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path: str):
        if path == "/" or not path:
            file_path = FRONTEND_DIR / "index.html"
        else:
            relative_path = path.lstrip("/")
            file_path = FRONTEND_DIR / relative_path

        # Security check: resolve path and verify it stays inside FRONTEND_DIR
        try:
            resolved = file_path.resolve()
            if not str(resolved).startswith(str(FRONTEND_DIR.resolve())):
                self._handle_json_response({"error": "Forbidden"}, status=403)
                return
        except Exception:
            self._handle_json_response({"error": "Invalid path"}, status=400)
            return

        if not file_path.exists() or file_path.is_dir():
            # Fallback to index.html for SPA routing if requested resource isn't found
            file_path = FRONTEND_DIR / "index.html"

        mime_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon"
        }

        ext = file_path.suffix.lower()
        content_type = mime_types.get(ext, "application/octet-stream")

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as exc:
            self._handle_json_response({"error": f"Failed to serve file: {str(exc)}"}, status=500)

    def log_message(self, format, *args):
        # Concise server request logging
        sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def create_server(port: int = 8000, host: str = "127.0.0.1") -> http.server.ThreadingHTTPServer:
    server_address = (host, port)
    return http.server.ThreadingHTTPServer(server_address, PortfolioAnalyticsHandler)


def run_server(port: int = 8000, host: str = "127.0.0.1"):
    httpd = create_server(port=port, host=host)
    print(f"Server started cleanly at http://{host}:{port}")
    print("Serving Smart Investment & Portfolio Analytics Dashboard...")
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down server gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    run_server(port=port, host=host)
