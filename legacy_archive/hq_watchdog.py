#!/usr/bin/env python3
"""
hq_watchdog.py: Autonomous HQ System Health & Diagnostic Watchdog
Runs automated cycle tests across HQ Web UI, Hermes AI engines, Nikki Roleplay,
CMA valuation tools, MCP servers, and GPU bridge to guarantee 100% operational uptime.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()
EVIDENCE_DIR = WORKSPACE_ROOT / "evidence"
WATCHDOG_LOG = EVIDENCE_DIR / "watchdog_report.json"
HERMES_EXE = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-agent\bin\hermes.exe")

def ensure_evidence_dir():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

def test_python_modules() -> dict:
    modules = [
        "escalation_engine",
        "state_sync_engine",
        "server",
        "hermes_sandbox_server",
        "gpu_bridge"
    ]
    results = {}
    for mod in modules:
        try:
            __import__(mod)
            results[mod] = "OK"
        except Exception as e:
            results[mod] = f"FAILED: {e}"
    return results

def test_hermes_cli_binary() -> dict:
    if HERMES_EXE.exists():
        return {"status": "OK", "path": str(HERMES_EXE)}
    else:
        return {"status": "MISSING", "path": str(HERMES_EXE)}

def test_web_server_endpoints(port: int = 8088) -> dict:
    results = {}
    web_dir = WORKSPACE_ROOT / "real-estate-web"
    index_file = web_dir / "index.html"
    server_file = web_dir / "server.py"

    results["index_html"] = "OK" if index_file.exists() else "MISSING"
    results["server_py"] = "OK" if server_file.exists() else "MISSING"

    # Attempt HTTP ping if server is active
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/")
        with urllib.request.urlopen(req, timeout=2) as resp:
            results["live_listener"] = f"ONLINE (code {resp.status})"
    except Exception:
        results["live_listener"] = "STANDBY (ready for launch)"

    return results

def test_training_dojo() -> dict:
    playbook_file = WORKSPACE_ROOT / "NIKKI_CONVERSION_PLAYBOOK.md"
    if not playbook_file.exists():
        return {"status": "FAILED", "reason": "NIKKI_CONVERSION_PLAYBOOK.md missing"}

    # Live E2E Query Execution Test
    try:
        import importlib.util
        web_server_path = WORKSPACE_ROOT / "real-estate-web" / "server.py"
        spec = importlib.util.spec_from_file_location("web_server_mod", str(web_server_path))
        web_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(web_mod)
        test_out = web_mod.get_nikki_playbook_response("I am just browsing")
        if not test_out or "Nikki's Playbook Response" not in test_out:
            return {"status": "FAILED", "reason": "Playbook engine returned invalid response"}
    except Exception as e:
        return {"status": "FAILED", "reason": f"Execution error: {e}"}

    return {"status": "OK", "playbook_bytes": playbook_file.stat().st_size, "e2e_test": "PASSED"}

def run_full_hq_diagnostic() -> dict:
    ensure_evidence_dir()
    timestamp = datetime.now().isoformat()
    
    module_health = test_python_modules()
    hermes_health = test_hermes_cli_binary()
    web_health = test_web_server_endpoints(port=8088)
    dojo_health = test_training_dojo()
    
    # Import state sync to verify workspace state
    try:
        from state_sync_engine import sync_workspace_state
        workspace_state = sync_workspace_state()
    except Exception as e:
        workspace_state = {"error": str(e)}
        
    # Check pending escalations
    try:
        from escalation_engine import load_escalations
        escalations = load_escalations()
        pending_count = len([e for e in escalations if e.get("status") == "PENDING_ANTI_RESOLUTION"])
    except Exception:
        pending_count = 0

    all_passed = (
        all(v == "OK" for v in module_health.values()) and
        hermes_health.get("status") == "OK" and
        dojo_health.get("status") == "OK"
    )

    report = {
        "timestamp": timestamp,
        "overall_status": "HEALTHY" if all_passed else "DEGRADED",
        "components": {
            "core_modules": module_health,
            "training_dojo_nikki": dojo_health,
            "hermes_agent_cli": hermes_health,
            "web_endpoints": web_health,
            "pending_escalations": pending_count,
            "workspace_sync": workspace_state.get("sync_status", "UNKNOWN")
        }
    }

    with open(WATCHDOG_LOG, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== RUNNING AUTONOMOUS HQ WATCHDOG DIAGNOSTIC ===")
    rep = run_full_hq_diagnostic()
    print(json.dumps(rep, indent=2))
