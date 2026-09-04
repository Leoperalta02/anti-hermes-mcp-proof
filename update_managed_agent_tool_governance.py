"""
write_managed_agent_tool.py
Writes the complete fail-closed managed_agent_tool.py file.
"""
code = '''"""Tool for sending structured, authenticated messages to named Buzz managed agents."""

import contextvars
import json
import logging
from pathlib import Path
from typing import Any, Optional, Set, Tuple

from tools.registry import registry

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# #panel-advisors HARD TOOL LOCK & GOVERNANCE CONTEXT
# ---------------------------------------------------------------------------
_PANEL_BLOCKED_CHANNEL_NAMES = {"panel-advisors"}
_PANEL_BLOCKED_CHANNEL_IDS  = {"297db211-a6d3-4544-97f2-940b55e85284"}

_PANEL_ROUTABLE_PUBKEYS = {
    "grok 2": "7f7a088edf2bc7f02a0c47e2e162efa863631dff06a126246a38493e7cd9e235",
    "grok": "7f7a088edf2bc7f02a0c47e2e162efa863631dff06a126246a38493e7cd9e235",
    "cursor pro": "2cf56b3bf472df0a9ff819a86d8f84ad24e405f444af0a2d491173cfb32ea8e1",
    "cursor": "2cf56b3bf472df0a9ff819a86d8f84ad24e405f444af0a2d491173cfb32ea8e1",
}

# Verified active channel members in #panel-advisors
_PANEL_VERIFIED_MEMBER_PUBKEYS = {
    "7f7a088edf2bc7f02a0c47e2e162efa863631dff06a126246a38493e7cd9e235", # Grok 2
    "2cf56b3bf472df0a9ff819a86d8f84ad24e405f444af0a2d491173cfb32ea8e1", # Cursor Pro
}

# ContextVar for active channel context: (channel_name, channel_id)
_current_channel_ctx: contextvars.ContextVar[Optional[Tuple[str, str]]] = contextvars.ContextVar(
    "_current_channel_ctx", default=None
)

# ContextVar for seats explicitly named by Leo for the current active round
_active_round_named_seats: contextvars.ContextVar[Optional[Set[str]]] = contextvars.ContextVar(
    "_active_round_named_seats", default=None
)

def set_current_channel(channel_name: str, channel_id: str) -> None:
    """Called by ACP server when channel context is established."""
    _current_channel_ctx.set((channel_name.lower().strip(), channel_id.lower().strip()))

def set_active_round_seats(named_seats: Set[str]) -> None:
    """Called by ACP server when a round opener sets named target seats."""
    cleaned = {s.lower().strip() for s in named_seats}
    _active_round_named_seats.set(cleaned)

def _is_panel_channel() -> bool:
    """Return True if current channel is panel-advisors."""
    val = _current_channel_ctx.get()
    if val is None:
        return False
    name, cid = val
    return name in _PANEL_BLOCKED_CHANNEL_NAMES or cid in _PANEL_BLOCKED_CHANNEL_IDS


def _is_alienware_hq_hold_active() -> bool:
    """Fail-closed: HOLD active unless evidence/operator_gates.json records lift."""
    candidates = [
        Path(r"C:\\LEO-LAB-ANTIGRAVITY\\anti-hermes-mcp-proof\\evidence\\operator_gates.json"),
        Path(__file__).resolve().parents[2] / "evidence" / "operator_gates.json",
    ]
    for gates_path in candidates:
        try:
            if gates_path.exists():
                data = json.loads(gates_path.read_text(encoding="utf-8"))
                gates = data.get("gates") if isinstance(data.get("gates"), dict) else {}
                return bool(gates.get("alienware_hq_hold_active", True))
        except Exception:
            continue
    return True


# ---------------------------------------------------------------------------
# send_managed_agent — HARD BLOCKED IN #panel-advisors
# ---------------------------------------------------------------------------

MANAGED_AGENT_TOOL_SCHEMA = {
    "name": "send_managed_agent",
    "description": (
        "Send an authenticated message to another real Buzz managed agent via the Buzz supervisor. "
        "BLOCKED in #panel-advisors channel."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "target_agent": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["target_agent", "content"],
    },
}

def send_managed_agent(raw_args: Any) -> str:
    """Send structured message to another managed agent via the supervisor's ACP extension."""
    if _is_panel_channel():
        block_msg = "[STOP — TOOL DENY] send_managed_agent is blocked in #panel-advisors. Routing must be in-channel @ only. Escalate to Leo."
        logger.warning("PANEL TOOL DENY: send_managed_agent called in panel-advisors channel — blocked.")
        return block_msg

    ch_val = _current_channel_ctx.get()
    if ch_val:
        ch_name, _ = ch_val
        if ch_name in {"alienware-hq", "#alienware-hq"} and _is_alienware_hq_hold_active():
            block_msg = "[STOP — HOLD ACTIVE] send_managed_agent is blocked in #Alienware-hq. Practice hops only in #wellington-canary or #rosie-onboarding-sandbox."
            logger.warning("HOLD ACTIVE DENY: send_managed_agent called in #Alienware-hq — blocked.")
            return block_msg

    parsed_args: dict = {}
    if isinstance(raw_args, str):
        try:
            loaded = json.loads(raw_args)
            if isinstance(loaded, dict):
                parsed_args = loaded
        except Exception:
            pass
    elif isinstance(raw_args, dict):
        parsed_args = raw_args

    target_clean = str(parsed_args.get("target_agent") or "").strip()
    content_clean = str(parsed_args.get("content") or "").strip()

    if not target_clean or not content_clean:
        return "Error: target_agent and content parameters are required."

    _SANDBOX_CHANNELS = {"wellington-canary", "#wellington-canary", "rosie-onboarding-sandbox", "#rosie-onboarding-sandbox"}
    _SPECIALIST_AGENTS = {"harbor", "keystone", "quill", "rosie"}
    if target_clean.lower() in _SPECIALIST_AGENTS:
        if not ch_val or ch_val[0].lower() not in _SANDBOX_CHANNELS:
            block_msg = f"[STOP — SANDBOX VIOLATION] Specialist '{target_clean}' can only be delegated to in sandbox channels: {_SANDBOX_CHANNELS}."
            logger.warning(block_msg)
            return block_msg

    from acp_adapter.server import get_acp_requester
    requester = get_acp_requester()
    if not requester:
        return "Error: ACP connection not active or supervisor communication is unavailable."

    try:
        payload = {"target_agent": target_clean, "content": content_clean}
        res = requester("_buzz/send_managed_agent", payload)
        if isinstance(res, dict) and "error" in res:
            return f"Relay error sending to {target_clean}: {res['error']}"
        event_id = None
        if isinstance(res, dict):
            event_id = res.get("delegation_event_id") or res.get("event_id") or res.get("message_id")
            
        if not event_id or event_id == "unknown":
            return f"[STOP — NO EVENT ID: {target_clean}]"
            
        return f"Delegation Event ID: {event_id}\\nStatus: Message published successfully to {target_clean}.\\nCRITICAL: You MUST preserve this event_id and include it in your final summary report for {target_clean} exactly formatted as '{target_clean}: <status> | event_id: {event_id}'."
    except Exception as e:
        return f"Relay exception communicating with supervisor: {e}"

def _handler(args: Any, **kw) -> str:
    return send_managed_agent(raw_args=args)

registry.register(
    name="send_managed_agent",
    toolset="buzz_ipc",
    schema=MANAGED_AGENT_TOOL_SCHEMA,
    handler=_handler,
    emoji="📡",
)


# ---------------------------------------------------------------------------
# mention_agent_in_channel — Supervisor-Mediated In-Channel Mention Tool
# ---------------------------------------------------------------------------

MENTION_AGENT_TOOL_SCHEMA = {
    "name": "mention_agent_in_channel",
    "description": (
        "Publish a structured, in-channel @mention to an allowlisted advisor seat (e.g. 'Grok 2' or 'Cursor Pro') via the Buzz supervisor. "
        "Requires target seat to be named in the active round_id and verified member of #panel-advisors. Returns event_id."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "target_agent": {
                "type": "string",
                "description": "The exact name of the target advisor seat (e.g. 'Grok 2', 'Cursor Pro'). Must be an allowlisted member of the current round.",
            },
            "message": {
                "type": "string",
                "description": "The message or round question text to deliver with the in-channel mention.",
            },
        },
        "required": ["target_agent", "message"],
    },
}

def mention_agent_in_channel(raw_args: Any) -> str:
    \"\"\"Publish a structured in-channel mention to an allowlisted panel seat via supervisor's mention endpoint.\"\"\"
    # Governance Rule 5: Scope Lock — Fail closed outside #panel-advisors
    if not _is_panel_channel():
        return "[STOP — NON-PANEL CHANNEL] mention_agent_in_channel is restricted to #panel-advisors during this pilot."

    parsed_args: dict = {}
    if isinstance(raw_args, str):
        try:
            loaded = json.loads(raw_args)
            if isinstance(loaded, dict):
                parsed_args = loaded
        except Exception:
            pass
    elif isinstance(raw_args, dict):
        parsed_args = raw_args

    target_raw = str(parsed_args.get("target_agent") or "").strip()
    message_raw = str(parsed_args.get("message") or "").strip()

    if not target_raw or not message_raw:
        return "Error: target_agent and message parameters are required and cannot be empty."

    target_key = target_raw.lower()
    target_pubkey = _PANEL_ROUTABLE_PUBKEYS.get(target_key)

    # Governance Rule 2: Current-round enforcement
    active_named = _active_round_named_seats.get()
    if active_named is not None:
        if target_key not in active_named and target_raw.lower() not in active_named:
            return f"[ROUTE REJECT] Target '{target_raw}' is not named in the active round_id."

    if not target_pubkey:
        return f"[ROUTE REJECT] Target '{target_raw}' is not an allowlisted routable seat in #panel-advisors."

    # Governance Rule 3: Channel Membership verification
    if target_pubkey not in _PANEL_VERIFIED_MEMBER_PUBKEYS:
        return f"[NO ROUTE] Target '{target_raw}' (pubkey: {target_pubkey}) is not a verified member of #panel-advisors."

    from acp_adapter.server import get_acp_requester
    requester = get_acp_requester()
    if not requester:
        return "Error: ACP connection not active or supervisor communication is unavailable."

    try:
        # Governance Rule 1: Mention-Only Hard Branch — No Managed Task Delegation
        payload = {
            "action": "in_channel_mention_only",
            "in_channel_mention_only": True,
            "is_task_delegation": False,
            "target_agent": target_raw,
            "target_pubkey": target_pubkey,
            "message": message_raw,
            "content": message_raw,
        }
        res = requester("_buzz/publish_in_channel_mention", payload)
        
        # Fallback to _buzz/send_managed_agent only if _buzz/publish_in_channel_mention is not registered,
        # but with explicit in_channel_mention_only=True flag
        if isinstance(res, dict) and res.get("error", {}).get("code") == -32601:
            res = requester("_buzz/send_managed_agent", payload)

        if isinstance(res, dict) and "error" in res:
            err_msg = res["error"].get("message", str(res["error"]))
            return f"Relay error sending mention to {target_raw}: {err_msg}"

        # Governance Rule 4: Strict Event ID Traceability
        event_id = None
        if isinstance(res, dict):
            event_id = res.get("delegation_event_id") or res.get("event_id") or res.get("message_id")

        if not event_id or event_id == "unknown":
            return f"[STOP — NO EVENT ID] Supervisor failed to return a valid event_id for mention to {target_raw}."

        return (
            f"Structured Mention Sent: {target_raw}\\n"
            f"Target Pubkey: {target_pubkey}\\n"
            f"Delegation Event ID: {event_id}\\n"
            f"Status: Structured in-channel mention published successfully with Nostr p-tag."
        )
    except Exception as e:
        logger.exception("mention_agent_in_channel failed")
        return f"Relay exception sending mention to {target_raw}: {e}"

def _mention_handler(args: Any, **kw) -> str:
    return mention_agent_in_channel(raw_args=args)

registry.register(
    name="mention_agent_in_channel",
    toolset="buzz_ipc",
    schema=MENTION_AGENT_TOOL_SCHEMA,
    handler=_mention_handler,
    emoji="📢",
)
'''

target_file = r'C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\managed_agent_tool.py'
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(code)

print('Successfully wrote fail-closed managed_agent_tool.py!')
