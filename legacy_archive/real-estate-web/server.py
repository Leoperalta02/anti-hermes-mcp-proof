#!/usr/bin/env python3
"""
real-estate-web/server.py: Buzz AI / Alien Security MSP Web Server
Serves Buzz AI Security client web UI, handles SSE event streaming for Buzz Response Drawer,
and routes requests through buzz_security_core.py and buzzi_hermes_core.py.
"""

import http.server
import json
import os
import sys
import urllib.parse
from pathlib import Path

PARENT_DIR = Path(__file__).resolve().parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

import buzz_security_core
import buzzi_hermes_core
from escalation_engine import check_for_escalation, load_escalations
from hq_watchdog import run_full_hq_diagnostic

PORT = 8088
HTML_FILE = Path(__file__).resolve().parent / "index.html"

class BuzzSecurityServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        clean_path = parsed.path.rstrip("/")
        query_params = urllib.parse.parse_qs(parsed.query)

        if clean_path in ["", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open(HTML_FILE, "rb") as f:
                self.wfile.write(f.read())

        elif clean_path in ["/api/buzz/status", "/api/buzzi/status"]:
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            status_data = {
                "status": "ONLINE",
                "config": buzz_security_core.BUZZ_CONFIG,
                "vault_assets": buzz_security_core.check_vault_assets()
            }
            self.wfile.write(json.dumps(status_data, indent=2).encode("utf-8"))

        elif clean_path in ["/api/buzz/stream", "/api/buzzi/stream"]:
            query = query_params.get("query", [""])[0]
            category = query_params.get("category", ["bodyguard"])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            try:
                for evt in buzz_security_core.stream_buzz_security_event(query, category):
                    data_str = json.dumps(evt)
                    self.wfile.write(f"data: {data_str}\n\n".encode("utf-8"))
                    self.wfile.flush()
            except Exception as e:
                err_data = json.dumps({"event": "error", "message": str(e)})
                self.wfile.write(f"data: {err_data}\n\n".encode("utf-8"))

        elif clean_path == "/api/escalations":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            escs = load_escalations()
            self.wfile.write(json.dumps({"escalations": escs}).encode("utf-8"))

        elif clean_path == "/api/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            diag = run_full_hq_diagnostic()
            self.wfile.write(json.dumps(diag).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length).decode("utf-8")
        data = json.loads(raw_body) if raw_body else {}

        clean_path = self.path.split("?")[0].rstrip("/")

        if clean_path == "/api/buzz/security/scan":
            sender = data.get("sender", "unknown@domain.com")
            subject = data.get("subject", "Inbound Message")
            body = data.get("body", data.get("query", ""))
            attachments = data.get("attachments", [])

            scan_res = buzz_security_core.pre_screen_email_or_link(sender, subject, body, attachments)
            prov = buzz_security_core.format_provenance_banner(role="Buzz Guard (Bodyguard)")

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "provenance": prov,
                "scan_result": scan_res,
                "config": buzz_security_core.BUZZ_CONFIG
            }).encode("utf-8"))

        elif clean_path == "/api/buzz/pr/review":
            title = data.get("title", "Pull Request Analysis")
            diff = data.get("diff", data.get("query", ""))
            file_path = data.get("file_path", "src/main.py")

            review_res = buzz_security_core.review_pull_request_code(title, diff, file_path)
            prov = buzz_security_core.format_provenance_banner(role="Jit AppSec Reviewer")

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "provenance": prov,
                "review_result": review_res,
                "config": buzz_security_core.BUZZ_CONFIG
            }).encode("utf-8"))

        elif clean_path in ["/api/chat", "/api/buzzi/chat"]:
            query = data.get("query", "")
            channel = data.get("channel", "bodyguard")

            if channel == "appsec":
                res_obj = buzz_security_core.review_pull_request_code("PR Review", query)
                raw_resp = json.dumps(res_obj, indent=2)
            elif channel == "soc":
                res_obj = buzz_security_core.triage_service_anomaly("Deployment Telemetry", query)
                raw_resp = json.dumps(res_obj, indent=2)
            else:
                res_obj = buzz_security_core.pre_screen_email_or_link("inbound@external.com", "Inbound Inspection", query)
                raw_resp = f"{res_obj['shield_badge']}\n\n**Recommendation:** {res_obj['recommendation']}\n\n**Findings:** {', '.join(res_obj['findings']) if res_obj['findings'] else 'None (Verified Safe)'}"

            prov = buzz_security_core.format_provenance_banner()
            full_resp = f"{prov}\n{raw_resp}"

            is_esc, final_msg, record = check_for_escalation(query, raw_resp, source_bot="Buzz AI Security Web App")
            resp_payload = {
                "response": full_resp,
                "raw_response": raw_resp,
                "provenance": prov,
                "is_escalated": is_esc,
                "escalation_ticket": record,
                "config": buzz_security_core.BUZZ_CONFIG
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(resp_payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"=== BUZZ AI / ALIEN SECURITY MSP WEB SERVER RUNNING ON PORT {PORT} ===")
    print(f"Drawer Forced Visible: {buzz_security_core.BUZZ_CONFIG['agent_drawer_visible']}")
    print(f"Event Streaming: {buzz_security_core.BUZZ_CONFIG['stream_events']}")
    server = http.server.HTTPServer(("0.0.0.0", PORT), BuzzSecurityServerHandler)
    server.serve_forever()
