#!/usr/bin/env python3
"""Local staged-brief receiver for the Apex Realtor front door.

Binds 127.0.0.1 only. Writes JSON + Markdown under
C:\\LEO-LAB-ANTIGRAVITY\\business-scope\\onboarding-briefs\\
Does not deploy agents, provision tenants, or claim a live portal.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8787
_DEFAULT_BRIEF_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\business-scope\onboarding-briefs")
_WORKSPACE_FALLBACK = Path(__file__).resolve().parent.parent / "evidence" / "onboarding-briefs"


def resolve_brief_dir() -> Path:
    env = os.getenv("APEX_BRIEF_DIR")
    if env:
        return Path(env)
    if _DEFAULT_BRIEF_DIR.parent.exists():
        return _DEFAULT_BRIEF_DIR
    return _WORKSPACE_FALLBACK


BRIEF_DIR = resolve_brief_dir()
MAX_BODY = 256_000
SECRET_RE = re.compile(
    r"(password|passwd|api[_-]?key|secret|token|bearer|authorization|"
    r"connection string|private[_-]?key)",
    re.IGNORECASE,
)
ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return cleaned[:48] or "unnamed"


def markdown_for(brief: dict, filename_stem: str) -> str:
    answers = brief.get("answers") or {}
    asked = brief.get("asked") or ""
    can_stage = brief.get("can_stage") or []
    needs = brief.get("needs_verification") or []
    optional = brief.get("optional") or []
    created = brief.get("created_at") or utc_now().isoformat()
    lines = [
        f"# Staged Realtor brief — {filename_stem}",
        "",
        f"- Status: staged (not deployed)",
        f"- Created: {created}",
        f"- Surface: public front door (local)",
        "",
        "## What was asked",
        "",
        asked or "_Not specified._",
        "",
        "## Answers",
        "",
    ]
    for key, value in answers.items():
        if isinstance(value, list):
            shown = ", ".join(str(item) for item in value) or "—"
        elif value in ("", None, False):
            shown = "—" if value in ("", None) else "no"
        else:
            shown = str(value)
        lines.append(f"- **{key}:** {shown}")
    lines.extend(["", "## What can be staged", ""])
    lines.extend([f"- {item}" for item in can_stage] or ["- Local brief only."])
    lines.extend(["", "## What needs verification", ""])
    lines.extend([f"- {item}" for item in needs] or ["- No third-party connection was attempted."])
    lines.extend(["", "## Optional", ""])
    lines.extend([f"- {item}" for item in optional] or ["- None noted."])
    lines.extend(
        [
            "",
            "## Claims that remain false",
            "",
            "- Agent deployed: no",
            "- Portal URL created: no",
            "- MLS / IDX / ShowingTime: no",
            "- Voice or calendar sync: no",
            "",
        ]
    )
    return "\n".join(lines)


def cors_origin(handler: BaseHTTPRequestHandler) -> str:
    origin = handler.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        return origin
    # Same-machine file/server origins used in staging.
    if origin.startswith("http://127.0.0.1:") or origin.startswith("http://localhost:"):
        return origin
    return "http://127.0.0.1:8000"


class BriefHandler(BaseHTTPRequestHandler):
    server_version = "ApexBriefReceiver/1.0"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        print("[%s] %s" % (utc_now().isoformat(), format % args))

    def _cors(self, origin: str | None = None) -> None:
        self.send_header("Access-Control-Allow-Origin", origin or cors_origin(self))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
        self.send_header("Cache-Control", "no-store")

    def _send(self, code: int, payload: dict, origin: str | None = None) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors(origin)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/health"):
            self._send(
                200,
                {
                    "ok": True,
                    "status": "staged-receiver",
                    "bind": f"{HOST}:{PORT}",
                    "brief_dir": str(BRIEF_DIR),
                    "deploys_agents": False,
                },
            )
            return
        self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in ("/briefs", "/brief", "/"):
            self._send(404, {"ok": False, "error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0 or length > MAX_BODY:
            self._send(413, {"ok": False, "error": "brief too large or empty"})
            return
        raw = self.rfile.read(length)
        try:
            brief = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send(400, {"ok": False, "error": "invalid json"})
            return
        if not isinstance(brief, dict):
            self._send(400, {"ok": False, "error": "brief must be an object"})
            return
        if SECRET_RE.search(json.dumps(brief)):
            self._send(
                400,
                {
                    "ok": False,
                    "error": "credentials are not accepted",
                    "hint": "Remove passwords, API keys, and tokens.",
                },
            )
            return

        brief["status"] = "staged"
        brief["kind"] = brief.get("kind") or "apex_realtor_onboarding_brief"
        brief["received_at"] = utc_now().isoformat()
        brief.setdefault(
            "claims",
            {
                "agent_deployed": False,
                "portal_created": False,
                "mls_connected": False,
                "voice_enabled": False,
                "calendar_synced": False,
            },
        )

        answers = brief.get("answers") if isinstance(brief.get("answers"), dict) else {}
        who = answers.get("full_name") or answers.get("brokerage") or "unnamed"
        stamp = utc_now().strftime("%Y%m%dT%H%M%SZ")
        stem = f"{stamp}-{slugify(str(who))}"
        BRIEF_DIR.mkdir(parents=True, exist_ok=True)
        json_path = BRIEF_DIR / f"{stem}.json"
        md_path = BRIEF_DIR / f"{stem}.md"
        json_path.write_text(json.dumps(brief, indent=2), encoding="utf-8")
        md_path.write_text(markdown_for(brief, stem), encoding="utf-8")

        # Trigger Hermes brief triage & Telegram alert staging (W1 & W2 SOP hook)
        try:
            from apex_core.brief_watcher import brief_watcher
            brief_watcher.triage_brief(json_path)
        except Exception as err:
            self.log_message("Hermes triage hook warning: %s", err)

        self._send(
            201,
            {
                "ok": True,
                "status": "staged",
                "message": "Staged brief received. No agent deployed.",
                "paths": {"json": str(json_path), "markdown": str(md_path)},
            },
        )


def run_server(host: str = HOST, port: int = PORT, brief_dir: Path | None = None) -> ThreadingHTTPServer:
    global BRIEF_DIR
    if brief_dir:
        BRIEF_DIR = Path(brief_dir)
    BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), BriefHandler)
    return server


def main() -> None:
    server = run_server(HOST, PORT)
    print(f"Apex staged brief receiver on http://{HOST}:{PORT}")
    print(f"Briefs directory: {BRIEF_DIR}")
    print("Does not deploy agents. Bind is loopback only.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping receiver.")
        server.server_close()


if __name__ == "__main__":
    main()
