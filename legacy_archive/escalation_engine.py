#!/usr/bin/env python3
"""
escalation_engine.py: Hermes-to-Anti Automated Escalation Engine
Catches Hermes refusals, tool/permission limitations, or execution failures,
logs a Red Alert escalation ticket, and provides formatted escalation output.
"""

import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()
EVIDENCE_DIR = WORKSPACE_ROOT / "evidence"
ESCALATIONS_FILE = EVIDENCE_DIR / "escalations.json"

REFUSAL_PATTERNS = [
    r"\[ESCALATE_TO_ANTI",
    r"cannot access",
    r"unable to access",
    r"don't have access",
    r"do not have access",
    r"as an ai",
    r"i cannot perform",
    r"i cannot search",
    r"i cannot fetch",
    r"i apologize, but",
    r"i'm sorry, but",
    r"error executing assistant",
    r"execution error",
    r"permission denied",
    r"cloud fallback failed"
]

def ensure_evidence_dir():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    if not ESCALATIONS_FILE.exists():
        with open(ESCALATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

def load_escalations() -> list:
    ensure_evidence_dir()
    try:
        with open(ESCALATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_escalations(escalations: list):
    ensure_evidence_dir()
    with open(ESCALATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(escalations, f, indent=2)

def check_for_escalation(prompt: str, response: str, source_bot: str = "Hermes") -> tuple[bool, str, dict]:
    """
    Analyzes prompt and response. If Hermes failed or refused, returns (True, formatted_message, escalation_record).
    Otherwise returns (False, response, None).
    """
    response_lower = response.lower()
    triggered_pattern = None

    for pattern in REFUSAL_PATTERNS:
        if re.search(pattern, response_lower):
            triggered_pattern = pattern
            break

    if not triggered_pattern:
        return False, response, None

    esc_id = f"esc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:4]}"
    timestamp = datetime.now().isoformat()

    escalation_record = {
        "id": esc_id,
        "timestamp": timestamp,
        "source": source_bot,
        "user_prompt": prompt,
        "raw_response": response,
        "trigger_pattern": triggered_pattern,
        "status": "PENDING_ANTI_RESOLUTION"
    }

    escalations = load_escalations()
    escalations.append(escalation_record)
    save_escalations(escalations)

    reason_snippet = response.strip().split("\n")[0][:120] if response else "Capability limitation hit."

    formatted_msg = (
        f"⚡ **[RED ALERT AUTO-ESCALATION TO ANTI]** ⚡\n"
        f"────────────────────────────────────────\n"
        f"🤖 **Sub-agent:** `{source_bot}` hit a barrier.\n"
        f"📋 **Ticket ID:** `{esc_id}`\n"
        f"⚠️ **Reason:** *{reason_snippet}*\n\n"
        f"🚀 **Action:** Task auto-escalated to Anti (Chief of Staff).\n"
        f"Anti has full workspace context & capabilities and will process this request."
    )

    return True, formatted_msg, escalation_record

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    test_prompt = "Find sales comps for 10450 Stoneybrook"
    test_resp = "I cannot access MLS databases directly."
    is_esc, msg, record = check_for_escalation(test_prompt, test_resp, "Rosie CoPilot")
    print("Is Escalation:", is_esc)
    print("Formatted Message:\n", msg)
