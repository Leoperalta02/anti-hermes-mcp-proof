"""
Apex Luxury AI — Gated Telegram Dispatch (W2 live path)
Stages all alerts to evidence JSON by default. Live Telegram send requires:
  APEX_TELEGRAM_LIVE=1  AND  APEX_TELEGRAM_BOT_TOKEN  (fail-closed otherwise)

SOP §12: staged posture claims remain false; live send is operator-gated, not auto-enabled.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EVIDENCE_DIR = WORKSPACE_ROOT / "evidence"

DEFAULT_CLAIMS: Dict[str, bool] = {
    "agent_deployed": False,
    "portal_created": False,
    "mls_connected": False,
    "published_live": False,
    "voice_enabled": False,
    "calendar_synced": False,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


from apex_core.operator_gates import is_telegram_live_enabled


def is_live_dispatch_enabled() -> bool:
    return is_telegram_live_enabled()


def parse_chat_id(target: str) -> str:
    """Parse `telegram:8349762599` or raw numeric chat id."""
    cleaned = (target or "").strip()
    if cleaned.lower().startswith("telegram:"):
        return cleaned.split(":", 1)[1].strip()
    return cleaned


def send_via_telegram_bot_api(token: str, chat_id: str, message: str) -> Dict[str, Any]:
    """Send message using Telegram Bot HTTP API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description") or "Telegram API returned ok=false")
    return payload


class TelegramDispatcher:
    """Fail-closed Telegram alert dispatcher with staged JSON fallback."""

    def __init__(
        self,
        evidence_dir: Optional[Path] = None,
        send_fn: Optional[Callable[[str, str, str], Dict[str, Any]]] = None,
    ):
        self.evidence_dir = Path(evidence_dir) if evidence_dir else DEFAULT_EVIDENCE_DIR
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.latest_file = self.evidence_dir / "telegram_dispatch_latest.json"
        self.log_file = self.evidence_dir / "telegram_dispatch_log.jsonl"
        self._send_fn = send_fn or send_via_telegram_bot_api

    def dispatch(self, alert_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Always stage alert payload. Attempt live send only when APEX_TELEGRAM_LIVE=1
        and APEX_TELEGRAM_BOT_TOKEN is configured.
        """
        channel = str(alert_payload.get("channel") or "")
        message = str(alert_payload.get("message") or "")
        brief_id = alert_payload.get("brief_id") or alert_payload.get("id") or "unknown"

        record: Dict[str, Any] = {
            "timestamp": utc_now_iso(),
            "brief_id": brief_id,
            "channel": channel,
            "dispatch_status": "STAGED_ONLY",
            "live_sent": False,
            "external_send_blocked": True,
            "claims": dict(DEFAULT_CLAIMS),
            "message_preview": message[:240],
        }

        staged = {
            **alert_payload,
            "dispatch": record,
            "staged_at": utc_now_iso(),
        }
        self.latest_file.write_text(json.dumps(staged, indent=2), encoding="utf-8")

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        if not is_live_dispatch_enabled():
            record["reason"] = "APEX_TELEGRAM_LIVE not enabled — JSON stage only"
            self._refresh_latest(staged, record)
            return record

        token = os.getenv("APEX_TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            record["dispatch_status"] = "LIVE_BLOCKED_NO_TOKEN"
            record["reason"] = "APEX_TELEGRAM_LIVE=1 but APEX_TELEGRAM_BOT_TOKEN missing"
            self._refresh_latest(staged, record)
            return record

        chat_id = parse_chat_id(channel)
        if not chat_id or not message:
            record["dispatch_status"] = "LIVE_BLOCKED_INVALID_TARGET"
            record["reason"] = "Missing chat id or message body"
            self._refresh_latest(staged, record)
            return record

        try:
            api_result = self._send_fn(token, chat_id, message)
            record["dispatch_status"] = "LIVE_SENT"
            record["live_sent"] = True
            record["telegram_message_id"] = (
                api_result.get("result", {}) or {}
            ).get("message_id")
            record["reason"] = "Live dispatch succeeded (operator gate open)"
        except (urllib.error.URLError, RuntimeError, OSError, ValueError) as exc:
            record["dispatch_status"] = "LIVE_SEND_FAILED"
            record["reason"] = str(exc)

        self._refresh_latest(staged, record)
        return record

    def _refresh_latest(self, staged: Dict[str, Any], record: Dict[str, Any]) -> None:
        staged["dispatch"] = record
        self.latest_file.write_text(json.dumps(staged, indent=2), encoding="utf-8")


telegram_dispatcher = TelegramDispatcher()


def dispatch_telegram_alert(
    alert_payload: Dict[str, Any],
    evidence_dir: Optional[Path] = None,
    send_fn: Optional[Callable[[str, str, str], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    dispatcher = TelegramDispatcher(evidence_dir=evidence_dir, send_fn=send_fn)
    return dispatcher.dispatch(alert_payload)
