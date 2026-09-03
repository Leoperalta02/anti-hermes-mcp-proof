"""
apex_tools_server.py
Local REST API server for Buzz agents (Orion, Hermes, etc.)
Runs on http://localhost:9000
Agents call HTTP endpoints instead of terminal commands.

Endpoints:
  GET  /gmail/inbox          - Latest 15 emails
  GET  /gmail/message/{id}   - Full email body
  POST /gmail/send           - Send email (body: {to, subject, body})
  GET  /calendar/events      - Upcoming 10 calendar events
  POST /calendar/create      - Create event (body: {title, start, end, description})
  GET  /health               - Server health check
"""
import json
import base64
import urllib.request
import urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from pathlib import Path
from email.mime.text import MIMEText

VAULT_TOKEN_PATH = Path(__file__).parent / "vault_backup" / "google_oauth_token.json"
PORT = 9000

# ── Token Management ──────────────────────────────────────────────────────────

_cached_token = None
_token_expiry = None

def get_access_token():
    global _cached_token, _token_expiry
    now = datetime.now(timezone.utc)

    # Refresh if no token or expiring in next 5 minutes
    if _cached_token and _token_expiry and ((_token_expiry - now).total_seconds() > 300):
        return _cached_token

    with open(VAULT_TOKEN_PATH, "r") as f:
        vault = json.load(f)

    payload = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "client_id":     vault["client_id"],
        "client_secret": vault["client_secret"],
        "refresh_token": vault["refresh_token"],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        _cached_token = result["access_token"]
        expires_in = result.get("expires_in", 3600)
        _token_expiry = datetime.now(timezone.utc).replace(
            second=datetime.now(timezone.utc).second + expires_in
        )

        # Persist updated token
        vault["token"] = _cached_token
        vault["expiry"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if "refresh_token" in result:
            vault["refresh_token"] = result["refresh_token"]
        with open(VAULT_TOKEN_PATH, "w") as f:
            json.dump(vault, f, indent=2)

    return _cached_token


def gapi_get(url):
    token = get_access_token()
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def gapi_post(url, body_dict):
    token = get_access_token()
    payload = json.dumps(body_dict).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Gmail Helpers ─────────────────────────────────────────────────────────────

def get_inbox(max_results=15):
    data = gapi_get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages"
        f"?maxResults={max_results}&labelIds=INBOX"
    )
    messages = []
    for m in data.get("messages", []):
        msg = gapi_get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{m['id']}"
            f"?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"
        )
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        messages.append({
            "id":      m["id"],
            "from":    headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date":    headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return messages


def get_message_body(msg_id):
    msg = gapi_get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=full"
    )
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    def extract_body(payload):
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            result = extract_body(part)
            if result:
                return result
        return ""

    return {
        "id":      msg_id,
        "from":    headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "date":    headers.get("Date", ""),
        "body":    extract_body(msg.get("payload", {})),
    }


def send_email(to, subject, body):
    mime = MIMEText(body)
    mime["to"]      = to
    mime["subject"] = subject
    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode("utf-8")
    return gapi_post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        {"raw": raw}
    )


# ── Calendar Helpers ──────────────────────────────────────────────────────────

def get_calendar_events(max_results=10):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = gapi_get(
        f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
        f"?maxResults={max_results}&orderBy=startTime&singleEvents=true&timeMin={now}"
    )
    events = []
    for ev in data.get("items", []):
        start = ev.get("start", {})
        events.append({
            "id":          ev.get("id"),
            "title":       ev.get("summary", ""),
            "start":       start.get("dateTime", start.get("date", "")),
            "end":         ev.get("end", {}).get("dateTime", ev.get("end", {}).get("date", "")),
            "description": ev.get("description", ""),
            "location":    ev.get("location", ""),
        })
    return events


def create_calendar_event(title, start, end, description=""):
    body = {
        "summary":     title,
        "description": description,
        "start":       {"dateTime": start, "timeZone": "America/New_York"},
        "end":         {"dateTime": end,   "timeZone": "America/New_York"},
    }
    return gapi_post(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events", body
    )


# ── HTTP Request Handler ──────────────────────────────────────────────────────

class ApexToolsHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status=500):
        self.send_json({"error": message}, status)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        try:
            if path == "/health":
                self.send_json({"status": "ok", "server": "Apex Tools API", "port": PORT})

            elif path == "/gmail/inbox":
                self.send_json({"emails": get_inbox()})

            elif path.startswith("/gmail/message/"):
                msg_id = path.split("/gmail/message/")[1]
                self.send_json(get_message_body(msg_id))

            elif path == "/calendar/events":
                self.send_json({"events": get_calendar_events()})

            else:
                self.send_error_json(f"Unknown endpoint: {path}", 404)

        except urllib.error.HTTPError as e:
            self.send_error_json(f"Google API error {e.code}: {e.read().decode()}")
        except Exception as e:
            self.send_error_json(str(e))

    def do_POST(self):
        path = self.path.rstrip("/")
        try:
            body = self.read_body()

            if path == "/gmail/send":
                result = send_email(body["to"], body["subject"], body["body"])
                self.send_json({"sent": True, "message_id": result.get("id")})

            elif path == "/calendar/create":
                result = create_calendar_event(
                    title=body["title"],
                    start=body["start"],
                    end=body["end"],
                    description=body.get("description", ""),
                )
                self.send_json({"created": True, "event_id": result.get("id"), "event": result})

            else:
                self.send_error_json(f"Unknown endpoint: {path}", 404)

        except KeyError as e:
            self.send_error_json(f"Missing required field: {e}", 400)
        except urllib.error.HTTPError as e:
            self.send_error_json(f"Google API error {e.code}: {e.read().decode()}")
        except Exception as e:
            self.send_error_json(str(e))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")


# ── Start Server ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"[Apex Tools API] Starting on http://localhost:{PORT}")
    print(f"[Apex Tools API] Endpoints:")
    print(f"  GET  http://localhost:{PORT}/health")
    print(f"  GET  http://localhost:{PORT}/gmail/inbox")
    print(f"  GET  http://localhost:{PORT}/gmail/message/{{id}}")
    print(f"  POST http://localhost:{PORT}/gmail/send         body: {{to, subject, body}}")
    print(f"  GET  http://localhost:{PORT}/calendar/events")
    print(f"  POST http://localhost:{PORT}/calendar/create    body: {{title, start, end, description}}")
    print()
    server = HTTPServer(("", PORT), ApexToolsHandler)
    server.serve_forever()
