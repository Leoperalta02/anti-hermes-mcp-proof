"""Keep a loopback reverse tunnel from the droplet to the HP brief receiver."""

from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import paramiko

HOST = "159.223.183.138"
USER = "root"
KEY = Path.home() / ".ssh" / "apex-edge"
REMOTE_BIND = ("127.0.0.1", 18787)
LOCAL_TARGET = ("127.0.0.1", 8787)


def _pipe(src, dst) -> None:
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            src.close()
        except Exception:
            pass
        try:
            dst.close()
        except Exception:
            pass


def _handle(channel) -> None:
    try:
        sock = socket.create_connection(LOCAL_TARGET, timeout=8)
    except OSError:
        channel.close()
        return
    left = threading.Thread(target=_pipe, args=(channel, sock), daemon=True)
    right = threading.Thread(target=_pipe, args=(sock, channel), daemon=True)
    left.start()
    right.start()


def serve_once() -> None:
    key = paramiko.RSAKey.from_private_key_file(str(KEY))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, pkey=key, allow_agent=False, look_for_keys=False, timeout=20)
    transport = client.get_transport()
    transport.request_port_forward(REMOTE_BIND[0], REMOTE_BIND[1])
    print("tunnel-up", flush=True)
    while transport.is_active():
        channel = transport.accept(30)
        if channel is None:
            continue
        threading.Thread(target=_handle, args=(channel,), daemon=True).start()
    client.close()


def main() -> None:
    while True:
        try:
            serve_once()
        except Exception as err:
            print(f"tunnel-down {err}", flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()
