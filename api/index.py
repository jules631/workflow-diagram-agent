from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Callable

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from workflow_diagram_agent.generator import build_executive_workflow_diagram

StartResponse = Callable[[str, list[tuple[str, str]]], None]


def _json_response(start_response: StartResponse, status: str, payload: dict[str, object]) -> list[bytes]:
    encoded = json.dumps(payload).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(encoded))),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("Access-Control-Allow-Methods", "GET,POST,OPTIONS"),
    ]
    start_response(status, headers)
    return [encoded]


def app(environ: dict[str, object], start_response: StartResponse) -> list[bytes]:
    method = str(environ.get("REQUEST_METHOD", "GET")).upper()

    if method == "OPTIONS":
        return _json_response(start_response, "204 No Content", {})

    if method == "GET":
        return _json_response(start_response, "200 OK", {"ok": True, "message": "POST JSON {\"text\": \"...\"} to /api"})

    if method != "POST":
        return _json_response(start_response, "405 Method Not Allowed", {"ok": False, "error": "Method not allowed"})

    try:
        content_length = int(str(environ.get("CONTENT_LENGTH") or "0"))
    except ValueError:
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": "Invalid Content-Length header"})

    stream = environ.get("wsgi.input")
    if not hasattr(stream, "read"):
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": "Missing request body"})

    raw_body = stream.read(content_length).decode("utf-8") if content_length > 0 else "{}"

    try:
        body = json.loads(raw_body) if raw_body else {}
    except json.JSONDecodeError:
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": "Request body must be valid JSON"})

    text = str(body.get("text", "")).strip()
    if not text:
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": "Field 'text' is required"})

    max_steps_raw = body.get("max_steps", 6)
    try:
        max_steps = int(max_steps_raw)
    except (TypeError, ValueError):
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": "Field 'max_steps' must be an integer"})

    try:
        diagram = build_executive_workflow_diagram(text=text, max_steps=max_steps)
    except ValueError as exc:
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": str(exc)})

    return _json_response(start_response, "200 OK", {"ok": True, "diagram": diagram})
