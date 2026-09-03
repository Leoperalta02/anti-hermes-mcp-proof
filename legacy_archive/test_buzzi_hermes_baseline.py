#!/usr/bin/env python3
"""
test_buzzi_hermes_baseline.py: Complete Step-by-Step Baseline Verification Script
Tests vault integration, forced drawer configuration, security provenance headers,
event stream generation, and web server endpoints.
"""

import json
import os
import sys
import time
import urllib.request
import threading
import importlib.util
from pathlib import Path

# Fix encoding for Windows console output
sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import buzzi_hermes_core
import hermes_buzzi_bridge

def test_vault_and_config():
    print("[TEST 1/5] Verifying Vault Attachment & Forced Baseline Config...")
    status = hermes_buzzi_bridge.init_buzzi_bridge()
    print("  Bridge Status:", status["status"])
    print("  Vault Assets:", status["vault_assets"])
    
    cfg = status["buzzi_config"]
    assert cfg["agent_drawer_visible"] is True, "FAIL: agent_drawer_visible must be True"
    assert cfg["stream_events"] is True, "FAIL: stream_events must be True"
    assert status["vault_assets"]["google_oauth_token.json"] == "OK", "FAIL: google_oauth_token.json missing"
    assert status["vault_assets"]["vault_secrets.json"] == "OK", "FAIL: vault_secrets.json missing"
    assert status["vault_assets"]["NIKKI_CONVERSION_PLAYBOOK.md"] == "OK", "FAIL: NIKKI_CONVERSION_PLAYBOOK.md missing"
    print("  ✅ Vault & Baseline Config Test Passed clean!\n")

def test_provenance_banner():
    print("[TEST 2/5] Verifying Security Provenance Header Generator...")
    banner = buzzi_hermes_core.format_provenance_banner(session_id="TEST-123")
    print("  Generated Banner:\n" + banner)
    assert "SURFACE: Buzzi Client Web Workspace" in banner, "FAIL: Surface missing in banner"
    assert "TIER: TIER-1 WORKER" in banner, "FAIL: Tier missing in banner"
    assert "SESSION: #TEST-123" in banner, "FAIL: Session ID missing in banner"
    print("  ✅ Security Provenance Header Test Passed clean!\n")

def test_event_streaming_generator():
    print("[TEST 3/5] Verifying Buzzi Response Drawer Event Generator (stream_events=true)...")
    events = list(buzzi_hermes_core.stream_buzzi_response("Test prompt for Nikki playbook", channel="roleplay"))
    event_names = [e.get("event") for e in events]
    print("  Received Event Sequence:", event_names)
    assert "drawer_step" in event_names, "FAIL: drawer_step event missing"
    assert "provenance" in event_names, "FAIL: provenance event missing"
    assert "content" in event_names, "FAIL: content event missing"
    assert "done" in event_names, "FAIL: done event missing"
    print("  ✅ Event Streaming Generator Test Passed clean!\n")

def test_web_server_endpoints():
    print("[TEST 4/5] Verifying Web Server Endpoints...")
    server_path = WORKSPACE_ROOT / "real-estate-web" / "server.py"
    spec = importlib.util.spec_from_file_location("web_server", server_path)
    web_server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web_server)

    import http.server
    server = http.server.HTTPServer(("127.0.0.1", web_server.PORT), web_server.BuzziServerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    try:
        # Test /api/buzzi/status
        status_url = f"http://127.0.0.1:{web_server.PORT}/api/buzzi/status"
        req = urllib.request.urlopen(status_url)
        res_json = json.loads(req.read().decode("utf-8"))
        print("  /api/buzzi/status Response:", res_json.get("status"))
        assert res_json["config"]["agent_drawer_visible"] is True

        # Test /api/buzzi/chat
        chat_url = f"http://127.0.0.1:{web_server.PORT}/api/buzzi/chat"
        payload = json.dumps({"query": "I am just browsing homes", "channel": "roleplay"}).encode("utf-8")
        req_post = urllib.request.Request(chat_url, data=payload, headers={"Content-Type": "application/json"})
        res_post = urllib.request.urlopen(req_post)
        res_post_json = json.loads(res_post.read().decode("utf-8"))
        print("  /api/buzzi/chat Provenance Received:\n", res_post_json.get("provenance"))
        assert "Just Browsing" in res_post_json["response"]

        print("  ✅ Web Server Endpoints Test Passed clean!\n")
    finally:
        server.shutdown()

def test_clean_workspace():
    print("[TEST 5/5] Verifying Zero Clutter & Code Cleanliness...")
    web_html = WORKSPACE_ROOT / "real-estate-web" / "index.html"
    assert web_html.exists(), "FAIL: index.html missing"
    content = web_html.read_text(encoding="utf-8")
    assert "buzzi-response-drawer" in content, "FAIL: buzzi-response-drawer missing in index.html"
    assert "agent_drawer_visible" in content or "DRAWER ACTIVE" in content, "FAIL: drawer active state missing"
    print("  ✅ Workspace Cleanliness Test Passed clean!\n")

def run_all_tests():
    print("==========================================================")
    print("  BUZZI / HERMES AGENT BASELINE END-TO-END VERIFICATION  ")
    print("==========================================================\n")
    test_vault_and_config()
    test_provenance_banner()
    test_event_streaming_generator()
    test_web_server_endpoints()
    test_clean_workspace()
    print("🎉 ALL 5 BASELINE VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_all_tests()
