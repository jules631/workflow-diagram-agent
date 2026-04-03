from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from workflow_diagram_agent.generator import build_executive_workflow_diagram


class handler(BaseHTTPRequestHandler):
    def _write_json(self, status_code: int, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        self._write_json(200, {"ok": True, "message": "POST workflow text to this endpoint"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._write_json(400, {"ok": False, "error": "Invalid Content-Length header"})
            return

        raw_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            body = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            self._write_json(400, {"ok": False, "error": "Request body must be valid JSON"})
            return

        text = str(body.get("text", "")).strip()
        if not text:
            self._write_json(400, {"ok": False, "error": "Field 'text' is required"})
            return

        max_steps_raw = body.get("max_steps", 6)
        try:
            max_steps = int(max_steps_raw)
        except (TypeError, ValueError):
            self._write_json(400, {"ok": False, "error": "Field 'max_steps' must be an integer"})
            return

        try:
            diagram = build_executive_workflow_diagram(text=text, max_steps=max_steps)
        except ValueError as exc:
            self._write_json(400, {"ok": False, "error": str(exc)})
            return

        self._write_json(200, {"ok": True, "diagram": diagram})
