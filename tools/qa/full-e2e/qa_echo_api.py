from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


HOST = "127.0.0.1"
PORT = 9101


class Handler(BaseHTTPRequestHandler):
    server_version = "ZunoQaEcho/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json({"status": "OK"})
            return
        if parsed.path == "/echo":
            query = parse_qs(parsed.query)
            self._json({"echo": query.get("message", [""])[0]})
            return
        self._json({"detail": "not found"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/echo":
            self._json({"detail": "not found"}, status=404)
            return
        length = int(self.headers.get("content-length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {"raw": raw.decode("utf-8", errors="replace")}
        self._json({"echo": payload})

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, payload: dict, *, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("access-control-allow-origin", "*")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"QA echo API listening on http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
