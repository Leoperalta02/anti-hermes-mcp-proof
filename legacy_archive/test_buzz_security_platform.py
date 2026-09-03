#!/usr/bin/env python3
"""
test_buzz_security_platform.py: End-to-End Verification Test Script
Tests Buzz Guard Bodyguard, Jit AppSec PR Reviewer, Sera Autonomous SOC Triager,
Security Provenance Banners, and Web Server Endpoints.
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

import buzz_security_core

def test_vault_and_config():
    print("[TEST 1/5] Verifying Vault Backup Assets & Buzz Security Config...")
    assets = buzz_security_core.check_vault_assets()
    print("  Vault Assets Status:", assets)
    assert assets["vault_secrets.json"] == "OK", "FAIL: vault_secrets.json missing"
    assert assets["google_oauth_token.json"] == "OK", "FAIL: google_oauth_token.json missing"
    assert buzz_security_core.BUZZ_CONFIG["agent_drawer_visible"] is True
    assert buzz_security_core.BUZZ_CONFIG["stream_events"] is True
    print("  ✅ Vault & Config Test Passed clean!\n")

def test_bodyguard_green_shield():
    print("[TEST 2/5] Verifying Personal AI Bodyguard ('Buzz Guard') Pre-Screening...")
    # Clean Email Test
    clean_res = buzz_security_core.pre_screen_email_or_link("hr@company.com", "Team Meeting", "Attached meeting notes.")
    print("  Clean Email Badge:", clean_res["shield_badge"])
    assert clean_res["status"] == "GREEN_SHIELD", "FAIL: Expected GREEN_SHIELD status for clean email"

    # Phishing Email Test
    phish_res = buzz_security_core.pre_screen_email_or_link("alert@bank-security.xyz", "Urgent Account Verification Required", "Verify account immediately or wire transfer funds.", ["invoice.exe"])
    print("  Phishing Email Badge:", phish_res["shield_badge"])
    assert phish_res["status"] == "RED_QUARANTINE", "FAIL: Expected RED_QUARANTINE status for phishing email"
    print("  ✅ Bodyguard Green Shield Pre-Screening Test Passed clean!\n")

def test_jit_appsec_pr_reviewer():
    print("[TEST 3/5] Verifying Jit-Inspired AppSec & PR Code Reviewer...")
    vulnerable_code = "aws_key = 'akias1234567890123456'\n pickle.loads(raw_data)\n eval(user_input)"
    review_res = buzz_security_core.review_pull_request_code("PR #102: Add Auth Module", vulnerable_code, "src/auth.py")
    print("  PR Security Status:", review_res["status"])
    print("  Vulnerabilities Found:", review_res["vulnerability_count"])
    print("  Automated Fix Patch:\n" + review_res["automated_fix_patch"])
    assert review_res["vulnerability_count"] >= 2, "FAIL: Expected vulnerabilities to be flagged"
    assert review_res["status"] == "CHANGES_REQUESTED", "FAIL: Expected CHANGES_REQUESTED"
    print("  ✅ Jit AppSec & PR Reviewer Test Passed clean!\n")

def test_sera_soc_triage():
    print("[TEST 4/5] Verifying Sera-Inspired Autonomous SOC Anomaly Triager...")
    log_snippet = "ERROR [DatabasePool] SQL syntax error near 'SELECT * FROM users WHERE id='' OR 1=1--'"
    triage_res = buzz_security_core.triage_service_anomaly("Database Anomaly", log_snippet)
    print("  Ticket ID:", triage_res["ticket_id"])
    print("  Severity:", triage_res["severity"])
    print("  Action Taken:", triage_res["action_taken"])
    assert triage_res["severity"] == "CRITICAL", "FAIL: Expected CRITICAL severity for SQL injection"
    print("  ✅ Sera SOC Anomaly Triager Test Passed clean!\n")

def test_web_server_endpoints():
    print("[TEST 5/5] Verifying Buzz AI Security Web Server Endpoints...")
    server_path = WORKSPACE_ROOT / "real-estate-web" / "server.py"
    spec = importlib.util.spec_from_file_location("web_server", server_path)
    web_server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web_server)

    import http.server
    server = http.server.HTTPServer(("127.0.0.1", web_server.PORT), web_server.BuzzSecurityServerHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    try:
        # Test /api/buzz/status
        status_url = f"http://127.0.0.1:{web_server.PORT}/api/buzz/status"
        req = urllib.request.urlopen(status_url)
        res_json = json.loads(req.read().decode("utf-8"))
        print("  /api/buzz/status Response:", res_json.get("status"))
        assert res_json["config"]["agent_drawer_visible"] is True

        # Test /api/buzz/security/scan
        scan_url = f"http://127.0.0.1:{web_server.PORT}/api/buzz/security/scan"
        payload = json.dumps({
            "sender": "partner@trusted-vendor.com",
            "subject": "Vendor Contract",
            "body": "Please find attached contract PDF for review."
        }).encode("utf-8")
        req_post = urllib.request.Request(scan_url, data=payload, headers={"Content-Type": "application/json"})
        res_post = urllib.request.urlopen(req_post)
        res_post_json = json.loads(res_post.read().decode("utf-8"))
        print("  /api/buzz/security/scan Shield Badge:", res_post_json["scan_result"]["shield_badge"])
        assert "GREEN SHIELD" in res_post_json["scan_result"]["shield_badge"]

        print("  ✅ Web Server Endpoints Test Passed clean!\n")
    finally:
        server.shutdown()

def run_all_tests():
    print("=================================================================")
    print("  BUZZ AI / ALIEN SECURITY MSP PLATFORM END-TO-END VERIFICATION  ")
    print("=================================================================\n")
    test_vault_and_config()
    test_bodyguard_green_shield()
    test_jit_appsec_pr_reviewer()
    test_sera_soc_triage()
    test_web_server_endpoints()
    print("🎉 ALL 5 BUZZ SECURITY PLATFORM TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_all_tests()
