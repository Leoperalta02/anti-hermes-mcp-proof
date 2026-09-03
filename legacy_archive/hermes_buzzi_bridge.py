#!/usr/bin/env python3
"""
hermes_buzzi_bridge.py: Clean Buzzi & Hermes Agent Integration Bridge
Attaches secured OAuth tokens, API secrets, and Nikki playbooks from vault_backup/.
Configures Buzzi client response drawer (agent_drawer_visible = True, stream_events = True).
"""

import json
import sys
from pathlib import Path
from buzzi_hermes_core import (
    BUZZI_CONFIG,
    check_vault_assets,
    load_vault_secrets,
    load_nikki_playbook,
    HERMES_EXE
)

def init_buzzi_bridge() -> dict:
    """Initializes clean Buzzi / Hermes bridge with side drawer response view enabled."""
    vault_status = check_vault_assets()
    all_ok = all(v == "OK" for v in vault_status.values())
    
    secrets = load_vault_secrets()
    playbook = load_nikki_playbook()

    config = BUZZI_CONFIG.copy()
    config["oauth_tokens_attached"] = (vault_status.get("google_oauth_token.json") == "OK")
    config["nikki_playbook_attached"] = (len(playbook) > 100)

    summary = {
        "status": "INITIALIZED" if all_ok else "PARTIAL_VAULT",
        "buzzi_config": config,
        "vault_assets": vault_status,
        "playbook_bytes": len(playbook),
        "hermes_exe_reachable": HERMES_EXE.exists()
    }
    return summary

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== INITIALIZING CLEAN BUZZI / HERMES AGENT BRIDGE ===")
    res = init_buzzi_bridge()
    print(json.dumps(res, indent=2))
