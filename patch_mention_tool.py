"""
patch_mention_tool.py
Appends mention_agent_in_channel tool to C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\managed_agent_tool.py
"""
import sys

path = r'C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\managed_agent_tool.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_tool_code = '''

# ---------------------------------------------------------------------------
# mention_agent_in_channel — Supervisor-Mediated In-Channel Mention Tool
# Enables Hermes to publish structured Nostr p-tag mentions to allowlisted panel seats.
# ---------------------------------------------------------------------------

_PANEL_ROUTABLE_PUBKEYS = {
    "grok 2": "7f7a088edf2bc7f02a0c47e2e162efa863631dff06a126246a38493e7cd9e235",
    "grok": "7f7a088edf2bc7f02a0c47e2e162efa863631dff06a126246a38493e7cd9e235",
    "cursor pro": "2cf56b3bf472df0a9ff819a86d8f84ad24e405f444af0a2d491173cfb32ea8e1",
    "cursor": "2cf56b3bf472df0a9ff819a86d8f84ad24e405f444af0a2d491173cfb32ea8e1",
}

MENTION_AGENT_TOOL_SCHEMA = {
    "name": "mention_agent_in_channel",
    "description": (
        "Publish a structured, in-channel @mention to an allowlisted advisor seat (e.g. 'Grok 2' or 'Cursor Pro') via the Buzz supervisor. "
        "The supervisor attaches the recipient's Nostr pubkey p-tag, signs it with your identity, and publishes it to the channel, "
        "triggering the target seat's wakeup event over the network. Returns the delegation event_id."
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
    \"\"\"Publish a structured in-channel mention to an allowlisted panel seat via the supervisor's ACP extension.\"\"\"
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
    if _is_panel_channel() and not target_pubkey:
        return f"[ROUTE REJECT] Target '{target_raw}' is not an allowlisted routable seat in #panel-advisors."

    from acp_adapter.server import get_acp_requester
    requester = get_acp_requester()
    if not requester:
        return "Error: ACP connection not active or supervisor communication is unavailable."

    try:
        payload = {
            "target_agent": target_raw,
            "target_pubkey": target_pubkey or "",
            "content": message_raw,
            "message": message_raw,
            "in_channel_mention": True,
        }
        res = requester("_buzz/send_managed_agent", payload)
        if isinstance(res, dict) and "error" in res:
            err_msg = res["error"].get("message", str(res["error"]))
            return f"Relay error sending mention to {target_raw}: {err_msg}"

        event_id = "unknown"
        if isinstance(res, dict):
            event_id = res.get("delegation_event_id") or res.get("event_id") or res.get("message_id") or "unknown"

        return (
            f"Structured Mention Sent: {target_raw}\\n"
            f"Target Pubkey: {target_pubkey or 'resolved'}\\n"
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

if 'mention_agent_in_channel' not in content:
    with open(path, 'a', encoding='utf-8') as f:
        f.write(new_tool_code)
    print('Successfully added mention_agent_in_channel to managed_agent_tool.py!')
else:
    print('mention_agent_in_channel is already present in managed_agent_tool.py!')
