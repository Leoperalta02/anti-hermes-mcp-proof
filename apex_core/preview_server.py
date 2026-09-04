"""
Apex Luxury AI — Persistent Multi-Threaded Local Preview Server
Serves workspace root at http://localhost:8000 with CORS and no-cache headers.
"""

import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class RobustHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def run_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    os.chdir(WORKSPACE_ROOT)
    return ThreadingHTTPServer((host, port), RobustHandler)


def main():
    server = run_server("0.0.0.0", 8000)
    print(f"[PreviewServer] Running at http://localhost:8000 (Root: {WORKSPACE_ROOT})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
