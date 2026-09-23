#!/usr/bin/env python3
"""Public edge for the DigitalOcean droplet.

Serves a small front door and forwards staged-brief JSON to the HP brief
receiver through a loopback reverse tunnel. It does not deploy agents,
open the house LAN, or store webhook secrets.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HOST = "0.0.0.0"
PORT = 80
UPSTREAM = "http://127.0.0.1:18787/brief"
MAX_BODY = 256_000
SOURCES = {"fub": "follow_up_boss", "meta": "meta", "gmail": "gmail"}

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Apex edge</title>
<style>
body { margin: 0; min-height: 100vh; display: grid; place-items: center; background: #090d16; color: #f8fafc; font-family: Georgia, serif; }
main { max-width: 36rem; padding: 2rem; }
h1 { font-weight: 500; font-size: 1.8rem; margin: 0 0 0.6rem; }
p { color: #94a3b8; line-height: 1.5; }
</style>
</head>
<body>
<main>
<h1>Apex public edge</h1>
<p>This host accepts public intake and webhooks. Payloads are staged on the HP brief receiver. Nothing here deploys an agent.</p>
</main>
</body>
</html>
"""


def _forward(body: bytes) -> tuple[int, bytes]:
    request = Request(UPSTREAM, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=8) as response:
            return response.status, response.read()
    except HTTPError as err:
        return err.code, err.read()
    except URLError:
        payload = json.dumps({"ok": False, "error": "brief receiver tunnel is down"}).encode()
        return 502, payload


class EdgeHandler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send(200, b'{"ok":true,"role":"apex-public-edge"}', "application/json")
            return
        if path in ("/", "/index.html"):
            self._send(200, PAGE.encode(), "text/html; charset=utf-8")
            return
        self._send(404, b'{"ok":false,"error":"not found"}', "application/json")

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0 or length > MAX_BODY:
            self._send(413, b'{"ok":false,"error":"body too large or empty"}', "application/json")
            return
        raw = self.rfile.read(length)
        if path in ("/brief", "/briefs", "/"):
            body = raw
        elif path.startswith("/webhook/"):
            source = SOURCES.get(path.rsplit("/", 1)[-1])
            if not source:
                self._send(404, b'{"ok":false,"error":"unknown webhook"}', "application/json")
                return
            try:
                incoming = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._send(400, b'{"ok":false,"error":"invalid json"}', "application/json")
                return
            body = json.dumps(
                {
                    "kind": "apex_webhook_ingress",
                    "source": source,
                    "answers": {"full_name": source},
                    "payload": incoming,
                }
            ).encode()
        else:
            self._send(404, b'{"ok":false,"error":"not found"}', "application/json")
            return
        status, upstream = _forward(body)
        content_type = "application/json" if upstream[:1] in (b"{", b"[") else "text/plain; charset=utf-8"
        self._send(status, upstream, content_type)

    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), EdgeHandler)
    print(f"Apex public edge on http://{HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
