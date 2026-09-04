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

def main():
    os.chdir(WORKSPACE_ROOT)
    server = ThreadingHTTPServer(("0.0.0.0", 8000), RobustHandler)
    print(f"[PreviewServer] Running at http://localhost:8000 (Root: {WORKSPACE_ROOT})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
