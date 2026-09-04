"""
Apex Luxury AI — Unified Local Dev Launcher
Starts preview (:8000), listing intake (:8765), and brief receiver (:8787) together.

Usage:
  python apex_core/dev_launcher.py

Rosie quick links (default ports):
  Front door:  http://127.0.0.1:8000/public_sites/rosie/index.html
  Portal:      http://127.0.0.1:8000/public_sites/rosie/portal.html#listings
  Intake form: http://127.0.0.1:8765/
"""

from __future__ import annotations

import argparse
import signal
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import List, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

DEFAULT_PREVIEW_PORT = 8000
DEFAULT_INTAKE_PORT = 8765
DEFAULT_BRIEF_PORT = 8787
DEFAULT_HOST = "127.0.0.1"


@dataclass
class ManagedServer:
    name: str
    host: str
    port: int
    server: Optional[ThreadingHTTPServer] = None
    thread: Optional[threading.Thread] = None
    health_path: str = "/"
    ready: bool = False

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}{self.health_path}"


def port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def wait_for_health(url: str, timeout_sec: float = 8.0) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                if 200 <= resp.status < 500:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.15)
    return False


def _serve(server: ThreadingHTTPServer, managed: ManagedServer) -> None:
    managed.ready = True
    server.serve_forever()


def start_preview(host: str, port: int) -> ManagedServer:
    from apex_core.preview_server import run_server

    managed = ManagedServer("preview", host, port, health_path="/public_sites/rosie/index.html")
    if not port_available(host, port):
        raise RuntimeError(f"Port {port} already in use for preview server.")

    server = run_server(host, port)
    managed.server = server
    managed.thread = threading.Thread(target=_serve, args=(server, managed), daemon=True, name="preview")
    managed.thread.start()
    return managed


def start_intake(host: str, port: int) -> ManagedServer:
    from apex_core.listing_intake_server import run_server

    managed = ManagedServer("intake", host, port, health_path="/api/listing/queue")
    if not port_available(host, port):
        raise RuntimeError(f"Port {port} already in use for listing intake server.")

    server = run_server(host, port)
    managed.server = server
    managed.thread = threading.Thread(target=_serve, args=(server, managed), daemon=True, name="intake")
    managed.thread.start()
    return managed


def start_brief(host: str, port: int, brief_dir: Optional[Path] = None) -> ManagedServer:
    from landing_page.brief_receiver import run_server

    managed = ManagedServer("brief", host, port, health_path="/health")
    if not port_available(host, port):
        raise RuntimeError(f"Port {port} already in use for brief receiver.")

    server = run_server(host, port, brief_dir=brief_dir)
    managed.server = server
    managed.thread = threading.Thread(target=_serve, args=(server, managed), daemon=True, name="brief")
    managed.thread.start()
    return managed


def launch_dev_stack(
    host: str = DEFAULT_HOST,
    preview_port: int = DEFAULT_PREVIEW_PORT,
    intake_port: int = DEFAULT_INTAKE_PORT,
    brief_port: int = DEFAULT_BRIEF_PORT,
    brief_dir: Optional[Path] = None,
    wait_ready: bool = True,
) -> List[ManagedServer]:
    """Start all local dev services and optionally wait until health checks pass."""
    servers = [
        start_preview(host, preview_port),
        start_intake(host, intake_port),
        start_brief(host, brief_port, brief_dir=brief_dir),
    ]

    if wait_ready:
        for managed in servers:
            if not wait_for_health(managed.url):
                shutdown_servers(servers)
                raise RuntimeError(f"{managed.name} failed health check at {managed.url}")

    return servers


def shutdown_servers(servers: List[ManagedServer]) -> None:
    for managed in servers:
        if managed.server:
            managed.server.shutdown()
            managed.server.server_close()
        if managed.thread and managed.thread.is_alive():
            managed.thread.join(timeout=2.0)


def print_banner(host: str, preview_port: int, intake_port: int, brief_port: int) -> None:
    print("\n" + "=" * 62)
    print("  Apex Sovereign Realtor OS — Unified Dev Stack")
    print("=" * 62)
    print(f"  Preview (static sites):  http://{host}:{preview_port}/public_sites/rosie/index.html")
    print(f"  Portal (Listings tab):   http://{host}:{preview_port}/public_sites/rosie/portal.html")
    print(f"  Listing intake API:      http://{host}:{intake_port}/api/listing/queue")
    print(f"  Listing intake form:     http://{host}:{intake_port}/")
    print(f"  Front-door brief POST:   http://{host}:{brief_port}/brief")
    print("  SOP §12: STAGED ONLY — no live MLS / no agent deploy claims")
    print("=" * 62 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch Apex unified local dev stack")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--preview-port", type=int, default=DEFAULT_PREVIEW_PORT)
    parser.add_argument("--intake-port", type=int, default=DEFAULT_INTAKE_PORT)
    parser.add_argument("--brief-port", type=int, default=DEFAULT_BRIEF_PORT)
    parser.add_argument("--brief-dir", default="", help="Override onboarding-briefs directory")
    args = parser.parse_args()

    brief_dir = Path(args.brief_dir) if args.brief_dir else None
    servers: List[ManagedServer] = []

    def _shutdown(*_args) -> None:
        print("\n[DevLauncher] Shutting down services…")
        shutdown_servers(servers)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    servers = launch_dev_stack(
        host=args.host,
        preview_port=args.preview_port,
        intake_port=args.intake_port,
        brief_port=args.brief_port,
        brief_dir=brief_dir,
    )
    print_banner(args.host, args.preview_port, args.intake_port, args.brief_port)
    print("[DevLauncher] All services ready. Press Ctrl+C to stop.\n")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
