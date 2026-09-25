#!/usr/bin/env python3
"""Bounded Hermes profile dispatch.

Runs `hermes -p <profile> -z <task>` as an argument list against the
installed Hermes 0.19.0 executable. This is not delegate_task.

Diagnostics go to hermes-state/logs/dispatch_profile_task.log.
MCP stdout is reserved for protocol traffic.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

HERMES_EXE = Path(r"C:\Program Files\Python312\Scripts\hermes.exe")
HERMES_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state")
WORK_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof")
DIAG_LOG = HERMES_ROOT / "logs" / "dispatch_profile_task.log"
LOCK_DIR = HERMES_ROOT / "locks"
# Aura stays off this path until her broker constraints are enforced here.
ALLOWED_PROFILES = (
    "atelier",
    "codex",
    "harbor",
    "keystone",
    "mosaic",
    "quill",
    "rowan",
    "scout",
)
TIMEOUT_SECONDS = 120
OUTPUT_LIMIT = 8000
CREATE_NO_WINDOW = 0x08000000


def _diag(message: str) -> None:
    DIAG_LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{stamp} {message}\n"
    with DIAG_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line)
    print(line, file=sys.stderr, end="")


def _clip(text: str) -> str:
    if len(text) <= OUTPUT_LIMIT:
        return text
    return text[:OUTPUT_LIMIT] + "\n...[truncated]"


def _session_for_marker(profile: str, marker: str) -> str | None:
    db = HERMES_ROOT / "profiles" / profile / "state.db"
    if not db.is_file():
        return None
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        row = con.execute(
            "SELECT session_id FROM messages WHERE content LIKE ? ORDER BY rowid DESC LIMIT 1",
            (f"%{marker}%",),
        ).fetchone()
    finally:
        con.close()
    return row[0] if row else None


def _session_cwd(profile: str, session_id: str) -> str | None:
    db = HERMES_ROOT / "profiles" / profile / "state.db"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        row = con.execute("SELECT cwd FROM sessions WHERE id = ?", (session_id,)).fetchone()
    finally:
        con.close()
    return row[0] if row else None


class _ProfileLock:
    def __init__(self, profile: str) -> None:
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
        self.path = LOCK_DIR / f"{profile}.lock"
        self.handle = None

    def acquire(self) -> bool:
        import msvcrt

        self.handle = self.path.open("a+")
        if self.handle.seek(0, os.SEEK_END) == 0:
            self.handle.write("0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            self.handle.close()
            self.handle = None
            return False

    def release(self) -> None:
        import msvcrt

        if self.handle is None:
            return
        try:
            self.handle.seek(0)
            msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self.handle.close()
            self.handle = None


def _descendants(pid: int) -> list[int]:
    import ctypes
    from ctypes import wintypes

    TH32CS_SNAPPROCESS = 0x00000002

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_char * 260),
        ]

    kernel32 = ctypes.windll.kernel32
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == -1:
        return []
    entry = PROCESSENTRY32()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
    children: dict[int, list[int]] = {}
    try:
        found = kernel32.Process32First(snapshot, ctypes.byref(entry))
        while found:
            children.setdefault(entry.th32ParentProcessID, []).append(entry.th32ProcessID)
            found = kernel32.Process32Next(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    ordered: list[int] = []

    def walk(parent: int) -> None:
        for child in children.get(parent, []):
            walk(child)
            ordered.append(child)

    walk(pid)
    return ordered


def _pids_alive(pids: list[int]) -> list[int]:
    import ctypes
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32
    query_limited = 0x1000
    still_active = 259
    alive: list[int] = []
    for target in pids:
        handle = kernel32.OpenProcess(query_limited, False, target)
        if not handle:
            continue
        code = wintypes.DWORD()
        running = bool(kernel32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == still_active
        kernel32.CloseHandle(handle)
        if running:
            alive.append(target)
    return alive


def _terminate_tree(pid: int) -> dict:
    import ctypes
    import time

    kernel32 = ctypes.windll.kernel32
    process_terminate = 0x0001
    targets = _descendants(pid) + [pid]
    killed: list[int] = []
    for target in targets:
        handle = kernel32.OpenProcess(process_terminate, False, target)
        if not handle:
            continue
        if kernel32.TerminateProcess(handle, 1):
            killed.append(target)
        kernel32.CloseHandle(handle)
    alive = targets
    for _ in range(20):
        alive = _pids_alive(targets)
        if not alive:
            break
        time.sleep(0.1)
    return {
        "killed": killed,
        "still_alive": alive,
        "cleanup_confirmed": len(alive) == 0,
    }


def dispatch_profile_task(profile: str, task: str, timeout_seconds: int = TIMEOUT_SECONDS) -> dict:
    """Run one whitelisted profile oneshot and return the marker-matched session."""
    profile = (profile or "").strip()
    task = (task or "").strip()
    marker = f"DISPATCH-{uuid.uuid4().hex[:12]}"
    _diag(f"start marker={marker} profile={profile!r} timeout={timeout_seconds}")
    if profile not in ALLOWED_PROFILES:
        _diag(f"reject marker={marker} reason=profile")
        return {"ok": False, "error": f"profile not allowed: {profile}", "marker": marker}
    if not task:
        _diag(f"reject marker={marker} reason=empty-task")
        return {"ok": False, "error": "task is empty", "marker": marker}
    if not HERMES_EXE.is_file():
        return {"ok": False, "error": f"hermes executable missing: {HERMES_EXE}", "marker": marker}
    if not WORK_DIR.is_dir():
        return {"ok": False, "error": f"work dir missing: {WORK_DIR}", "marker": marker}

    lock = _ProfileLock(profile)
    if not lock.acquire():
        _diag(f"reject marker={marker} reason=profile-locked profile={profile}")
        return {
            "ok": False,
            "error": f"profile busy: {profile}",
            "marker": marker,
            "profile": profile,
        }

    prompt = f"{marker}\n{task}"
    env = os.environ.copy()
    env["HERMES_HOME"] = str(HERMES_ROOT)
    command = [str(HERMES_EXE), "-p", profile, "-z", prompt]
    _diag(
        f"launch marker={marker} exe={HERMES_EXE} args=-p {profile} -z <task> "
        f"cwd={WORK_DIR} hermes_home={HERMES_ROOT} stdin=DEVNULL"
    )
    process = subprocess.Popen(
        command,
        cwd=str(WORK_DIR),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )
    _diag(f"child marker={marker} pid={process.pid}")
    try:
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            cleanup = _terminate_tree(process.pid)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                stdout, stderr = "", ""
            _diag(
                f"timeout marker={marker} pid={process.pid} "
                f"killed={cleanup['killed']} alive={cleanup['still_alive']}"
            )
            return {
                "ok": False,
                "error": f"timeout after {timeout_seconds}s",
                "marker": marker,
                "profile": profile,
                "cwd": str(WORK_DIR),
                "profile_home": str(HERMES_ROOT / "profiles" / profile),
                "exit_code": None,
                "stdout": _clip(stdout or ""),
                "stderr": _clip(stderr or ""),
                "session_id": None,
                "cleanup": cleanup,
            }
        session_id = _session_for_marker(profile, marker)
        _diag(
            f"exit marker={marker} pid={process.pid} code={process.returncode} "
            f"session={session_id}"
        )
        return {
            "ok": process.returncode == 0 and session_id is not None,
            "marker": marker,
            "profile": profile,
            "cwd": str(WORK_DIR),
            "profile_home": str(HERMES_ROOT / "profiles" / profile),
            "session_cwd": _session_cwd(profile, session_id) if session_id else None,
            "exit_code": process.returncode,
            "stdout": _clip(stdout or ""),
            "stderr": _clip(stderr or ""),
            "session_id": session_id,
        }
    finally:
        lock.release()
        _diag(f"unlock marker={marker} profile={profile}")


def _serve_mcp() -> None:
    from mcp.server.fastmcp import FastMCP

    _diag("mcp-server-start")
    mcp = FastMCP("dispatch-profile-task")

    @mcp.tool()
    def dispatch_profile_task_tool(profile: str, task: str) -> str:
        """Run hermes -p <profile> -z <task> for a whitelisted specialist profile.

        Allowed profiles: atelier, codex, harbor, keystone, mosaic, quill, rowan, scout.
        The process cwd is the anti-hermes-mcp-proof repo. Aura is not dispatched here.
        """
        return json.dumps(dispatch_profile_task(profile, task), ensure_ascii=False)

    mcp.run()


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--mcp":
        _serve_mcp()
        return 0
    if len(argv) != 2:
        print("usage: dispatch_profile_task.py <profile> <task>", file=sys.stderr)
        print("       dispatch_profile_task.py --mcp", file=sys.stderr)
        return 2
    result = dispatch_profile_task(argv[0], argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
