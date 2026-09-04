"""
Lightweight HTTP intake server for Listing & Media submissions.
Connects portal forms and team tools to ListingMediaAgent.process_intake_submission().

Endpoints:
  GET  /                      — intake form (HTML)
  GET  /api/listing/queue     — pending queue entries (?tenant=rosie)
  POST /api/listing/submit    — JSON payload → process_intake_submission()
  POST /api/listing/approve   — JSON {listing_id, tenant_slug?} → approve_for_showcase() + rebuild front door
  POST /api/listing/rebuild   — JSON {tenant_slug?} → rebuild front door from office_listings.json
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from apex_core.listing_media_agent import DEFAULT_CLAIMS, ListingMediaAgent

DEFAULT_PORT = 8765
INTAKE_FORM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gulf Pointe — Listing Media Intake</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
           background: #0a0a0d; color: #f5f5f7; max-width: 720px; margin: 2rem auto; padding: 0 1.5rem; }
    h1 { font-size: 1.5rem; font-weight: 600; }
    p.sub { color: #86868b; font-size: 0.9rem; margin-bottom: 1.5rem; }
    label { display: block; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em;
            color: #e5c890; margin: 0.75rem 0 0.35rem; }
    input, select, textarea { width: 100%; padding: 0.65rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
      background: rgba(255,255,255,0.04); color: #fff; font-size: 0.9rem; }
    button { margin-top: 1.25rem; padding: 0.75rem 1.5rem; border-radius: 980px; border: none;
      background: linear-gradient(135deg,#f7e7c4,#e5c890); color: #000; font-weight: 600; cursor: pointer; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
    #msg { margin-top: 1rem; font-size: 0.85rem; }
    .ok { color: #34d399; } .err { color: #f87171; }
  </style>
</head>
<body>
  <h1>Listing & Media Intake</h1>
  <p class="sub">Gulf Pointe / Rosie Rivera • Staged only — SOP §12 zero false claims</p>
  <form id="intake-form">
    <label>Title</label>
    <input name="title" required placeholder="Gulf Pointe Lanai Estate">
    <label>Address</label>
    <input name="address" required placeholder="101 Bella Terra Blvd, Estero, FL">
    <div class="row">
      <div><label>Subdivision</label><input name="subdivision" placeholder="West Bay Club"></div>
      <div><label>Price ($)</label><input name="price" type="number" required></div>
    </div>
    <label>Status</label>
    <select name="status" required>
      <option value="FOR_SALE">FOR SALE</option>
      <option value="UNDER_CONTRACT">UNDER CONTRACT</option>
      <option value="RECORD_SOLD">RECORD SOLD</option>
    </select>
    <div class="row">
      <div><label>Beds</label><input name="beds" type="number" value="4"></div>
      <div><label>Baths</label><input name="baths" value="3.5"></div>
    </div>
    <div class="row">
      <div><label>Sqft</label><input name="sqft" type="number" required></div>
      <div><label>Pool</label><select name="pool"><option value="true">Yes</option><option value="false">No</option></select></div>
    </div>
    <label>View / Waterfront</label>
    <input name="view" placeholder="Championship fairway / Gulf access">
    <label>Photo URLs (one per line)</label>
    <textarea name="photos" rows="3" required placeholder="https://..."></textarea>
    <label>Video URL (optional)</label>
    <input name="video_url" placeholder="https://...">
    <input type="hidden" name="tenant_slug" value="rosie">
    <button type="submit">Submit to Intake Queue</button>
  </form>
  <div id="msg"></div>
  <script>
    document.getElementById('intake-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const photos = (fd.get('photos') || '').split('\\n').map(s => s.trim()).filter(Boolean);
      const payload = {
        title: fd.get('title'), address: fd.get('address'), subdivision: fd.get('subdivision'),
        price: parseFloat(fd.get('price')), status: fd.get('status'),
        specs: { beds: parseInt(fd.get('beds')||4), baths: fd.get('baths'), sqft: parseInt(fd.get('sqft')),
                 pool: fd.get('pool') === 'true', view: fd.get('view') },
        photos, video_url: fd.get('video_url') || null, tenant_slug: fd.get('tenant_slug')
      };
      const msg = document.getElementById('msg');
      try {
        const res = await fetch('/api/listing/submit', { method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify(payload) });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Submit failed');
        msg.className = 'ok';
        msg.textContent = 'Queued: ' + data.listing_id + ' — awaiting portal approval.';
        e.target.reset();
      } catch (err) {
        msg.className = 'err';
        msg.textContent = err.message;
      }
    });
  </script>
</body>
</html>"""


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


class ListingIntakeHandler(BaseHTTPRequestHandler):
    agent: ListingMediaAgent = ListingMediaAgent()

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[ListingIntake] {self.address_string()} — {format % args}")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/intake"):
            body = INTAKE_FORM_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/api/listing/queue":
            qs = parse_qs(parsed.query)
            tenant = qs.get("tenant", [None])[0]
            pending = qs.get("pending", ["true"])[0].lower() != "false"
            queue = self.agent.load_intake_queue(tenant_slug=tenant, pending_only=pending)
            _json_response(self, 200, {"queue": queue, "claims": dict(DEFAULT_CLAIMS)})
            return

        _json_response(self, 404, {"error": "Not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            _json_response(self, 400, {"error": "Invalid JSON body"})
            return

        if parsed.path == "/api/listing/submit":
            try:
                result = self.agent.process_intake_submission(body)
                _json_response(self, 200, result)
            except ValueError as exc:
                _json_response(self, 400, {"error": str(exc), "claims": dict(DEFAULT_CLAIMS)})
            return

        if parsed.path == "/api/listing/approve":
            listing_id = str(body.get("listing_id", "")).strip()
            tenant_slug = str(body.get("tenant_slug") or "rosie").strip()
            if not listing_id:
                _json_response(self, 400, {"error": "listing_id required"})
                return
            try:
                result = self.agent.approve_for_showcase(listing_id)
                result["rebuild"] = self.agent.rebuild_front_door(tenant_slug)
                _json_response(self, 200, result)
            except ValueError as exc:
                _json_response(self, 400, {"error": str(exc), "claims": dict(DEFAULT_CLAIMS)})
            return

        if parsed.path == "/api/listing/rebuild":
            tenant_slug = str(body.get("tenant_slug") or "rosie").strip()
            try:
                result = self.agent.rebuild_front_door(tenant_slug)
                _json_response(self, 200, result)
            except ValueError as exc:
                _json_response(self, 400, {"error": str(exc), "claims": dict(DEFAULT_CLAIMS)})
            return

        _json_response(self, 404, {"error": "Not found"})


def create_handler(agent: Optional[ListingMediaAgent] = None) -> type:
    """Factory for tests with injectable agent instance."""
    handler_cls = type("ConfiguredListingIntakeHandler", (ListingIntakeHandler,), {})
    handler_cls.agent = agent or ListingMediaAgent()
    return handler_cls


def handle_request(
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
    agent: Optional[ListingMediaAgent] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Programmatic handler for unit tests without binding a port."""
    agent = agent or ListingMediaAgent()
    parsed = urlparse(path)

    if method == "GET" and parsed.path == "/api/listing/queue":
        qs = parse_qs(parsed.query)
        tenant = qs.get("tenant", [None])[0]
        queue = agent.load_intake_queue(tenant_slug=tenant, pending_only=True)
        return 200, {"queue": queue, "claims": dict(DEFAULT_CLAIMS)}

    if method == "POST" and parsed.path == "/api/listing/submit":
        try:
            return 200, agent.process_intake_submission(body or {})
        except ValueError as exc:
            return 400, {"error": str(exc), "claims": dict(DEFAULT_CLAIMS)}

    if method == "POST" and parsed.path == "/api/listing/approve":
        listing_id = str((body or {}).get("listing_id", "")).strip()
        tenant_slug = str((body or {}).get("tenant_slug") or "rosie").strip()
        if not listing_id:
            return 400, {"error": "listing_id required"}
        try:
            result = agent.approve_for_showcase(listing_id)
            rebuild = agent.rebuild_front_door(tenant_slug)
            result["rebuild"] = rebuild
            return 200, result
        except ValueError as exc:
            return 400, {"error": str(exc), "claims": dict(DEFAULT_CLAIMS)}

    if method == "POST" and parsed.path == "/api/listing/rebuild":
        tenant_slug = str((body or {}).get("tenant_slug") or "rosie").strip()
        try:
            return 200, agent.rebuild_front_door(tenant_slug)
        except ValueError as exc:
            return 400, {"error": str(exc), "claims": dict(DEFAULT_CLAIMS)}

    return 404, {"error": "Not found"}


def run_server(
    host: str = "127.0.0.1",
    port: int = DEFAULT_PORT,
    agent: Optional[ListingMediaAgent] = None,
) -> ThreadingHTTPServer:
    handler_cls = create_handler(agent)
    server = ThreadingHTTPServer((host, port), handler_cls)
    print(f"[ListingIntake] Serving on http://{host}:{port}/")
    return server


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Listing Media Intake Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    srv = run_server(host=args.host, port=args.port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[ListingIntake] Shutting down.")
        srv.shutdown()
