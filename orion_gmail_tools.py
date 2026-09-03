"""
orion_gmail_tools.py
Ready-to-use Gmail & Calendar tools for Orion.
Usage:
  python orion_gmail_tools.py summarize_emails
  python orion_gmail_tools.py read_calendar
  python orion_gmail_tools.py send_email --to EMAIL --subject SUBJECT --body BODY
"""
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone

VAULT_TOKEN_PATH = Path(__file__).parent / "vault_backup" / "google_oauth_token.json"

# ── Token Management ──────────────────────────────────────────────────────────

def load_and_refresh_token():
    """Load vault token, auto-refresh if expired, return valid access_token."""
    with open(VAULT_TOKEN_PATH, "r") as f:
        vault = json.load(f)

    # Always refresh to guarantee a live token
    payload = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "client_id":     vault["client_id"],
        "client_secret": vault["client_secret"],
        "refresh_token": vault["refresh_token"],
    }).encode("utf-8")

    req = urllib.request.Request(
        vault.get("token_uri", "https://oauth2.googleapis.com/token"),
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            access_token = result["access_token"]
            # Save fresh token back to vault
            vault["token"] = access_token
            vault["expiry"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            if "refresh_token" in result:
                vault["refresh_token"] = result["refresh_token"]
            with open(VAULT_TOKEN_PATH, "w") as f:
                json.dump(vault, f, indent=2)
            return access_token
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Token refresh failed: {e.read().decode()}")
        sys.exit(1)


def api_get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Gmail: Summarize Inbox ────────────────────────────────────────────────────

def summarize_emails():
    token = load_and_refresh_token()
    print("[*] Fetching latest 10 emails from inbox...\n")

    # List messages
    list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10&labelIds=INBOX"
    msg_list = api_get(list_url, token)
    messages = msg_list.get("messages", [])

    if not messages:
        print("Inbox is empty.")
        return

    print(f"{'#':<4} {'FROM':<35} {'SUBJECT':<50} {'DATE'}")
    print("-" * 110)

    for i, msg_ref in enumerate(messages, 1):
        msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_ref['id']}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=Date"
        msg = api_get(msg_url, token)
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        sender  = headers.get("From", "Unknown")[:34]
        subject = headers.get("Subject", "(no subject)")[:49]
        date    = headers.get("Date", "")[:25]
        print(f"{i:<4} {sender:<35} {subject:<50} {date}")

    print()


# ── Gmail: Send Email ─────────────────────────────────────────────────────────

def send_email(to, subject, body):
    import base64
    from email.mime.text import MIMEText

    token = load_and_refresh_token()
    print(f"[*] Sending email to {to}...")

    msg = MIMEText(body)
    msg["to"]      = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    payload = json.dumps({"raw": raw}).encode("utf-8")
    req = urllib.request.Request(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type":  "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"[OK] Email sent! Message ID: {result.get('id')}")
    except urllib.error.HTTPError as e:
        print(f"[ERROR] Send failed: {e.read().decode()}")


# ── Google Calendar: Read Events ──────────────────────────────────────────────

def read_calendar():
    token = load_and_refresh_token()
    now   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[*] Fetching upcoming calendar events...\n")

    url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=10&orderBy=startTime&singleEvents=true&timeMin={now}"
    data = api_get(url, token)
    events = data.get("items", [])

    if not events:
        print("No upcoming events found.")
        return

    print(f"{'#':<4} {'DATE/TIME':<25} {'TITLE'}")
    print("-" * 70)
    for i, ev in enumerate(events, 1):
        start = ev.get("start", {})
        dt    = start.get("dateTime", start.get("date", ""))[:19].replace("T", " ")
        title = ev.get("summary", "(no title)")
        print(f"{i:<4} {dt:<25} {title}")
    print()


# ── CLI Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python orion_gmail_tools.py summarize_emails")
        print("  python orion_gmail_tools.py read_calendar")
        print("  python orion_gmail_tools.py send_email --to EMAIL --subject SUBJECT --body BODY")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "summarize_emails":
        summarize_emails()

    elif cmd == "read_calendar":
        read_calendar()

    elif cmd == "send_email":
        args = sys.argv[2:]
        def get_arg(flag):
            try:
                return args[args.index(flag) + 1]
            except (ValueError, IndexError):
                print(f"[ERROR] Missing {flag}")
                sys.exit(1)
        send_email(
            to      = get_arg("--to"),
            subject = get_arg("--subject"),
            body    = get_arg("--body"),
        )

    else:
        print(f"[ERROR] Unknown command: {cmd}")
        sys.exit(1)
