"""SQLite Lease Guardian & Gateway Watchdog for Hermes State.

Ensures:
1. SQLite single-writer discipline by auto-purging expired session turn leases.
2. Per-profile Hermes Gateway liveness (active CoS profile + cursor) with WMI respawn.
3. Cursor CLI bridge (:4646) auto-heal.
4. Single guardian instance (PID lock).
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("lease_guardian")

DEFAULT_HERMES_HOME = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state")
DEFAULT_STATE_DB = DEFAULT_HERMES_HOME / "state.db"
HERMES_AGENT_ROOT = DEFAULT_HERMES_HOME / "hermes-agent"
HERMES_PYTHON = HERMES_AGENT_ROOT / "venv" / "Scripts" / "python.exe"
LOCK_PATH = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\evidence\lease_guardian.lock")
LOG_PATH = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\evidence\guardian.log")


def _resolve_primary_cos_profile() -> str:
    profiles_dir = DEFAULT_HERMES_HOME / "profiles"
    candidates = [os.getenv("HERMES_PROFILE", "").strip(), "Anti", "default", "anti-cos"]
    seen = set()
    for name in candidates:
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        if (profiles_dir / name).exists():
            return name
    return "Anti"


PRIMARY_COS_PROFILE = _resolve_primary_cos_profile()

# Profile gateways that must stay up for Telegram / room contact while Leo is AFK.
PROFILE_GATEWAYS = [
    {
        "name": PRIMARY_COS_PROFILE,
        "pid_file": DEFAULT_HERMES_HOME / "profiles" / PRIMARY_COS_PROFILE / "gateway.pid",
        "vbs": DEFAULT_HERMES_HOME
        / "profiles"
        / PRIMARY_COS_PROFILE
        / "gateway-service"
        / f"Hermes_Gateway_{PRIMARY_COS_PROFILE}.vbs",
        "workdir": DEFAULT_HERMES_HOME / "profiles" / PRIMARY_COS_PROFILE,
    },
    {
        "name": "cursor",
        "pid_file": DEFAULT_HERMES_HOME / "profiles" / "cursor" / "gateway.pid",
        "vbs": DEFAULT_HERMES_HOME
        / "profiles"
        / "cursor"
        / "gateway-service"
        / "Hermes_Gateway_cursor.vbs",
        "workdir": DEFAULT_HERMES_HOME / "profiles" / "cursor",
    },
]

# Legacy default-home launcher (fallback only).
LEGACY_GATEWAY_VBS = DEFAULT_HERMES_HOME / "gateway-service" / "Hermes_Gateway.vbs"

os.environ.setdefault("HERMES_HOME", str(DEFAULT_HERMES_HOME))

# Throttle for non-critical service warnings (seconds).
_WARN_LAST: Dict[str, float] = {}
_WARN_INTERVAL_SEC = 1800.0  # 30 min


def purge_stale_leases(db_path: Path = DEFAULT_STATE_DB, now: Optional[float] = None) -> int:
    """Purge expired session turn leases from state.db with strict single-transaction hygiene."""
    if not db_path.exists():
        logger.warning("state.db not found at %s", db_path)
        return 0

    if now is None:
        now = time.time()

    purged = 0
    conn = None
    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='session_turn_leases';"
        )
        if not cursor.fetchone():
            return 0

        cursor.execute("DELETE FROM session_turn_leases WHERE expires_at < ?;", (now,))
        purged = cursor.rowcount
        conn.commit()
    except sqlite3.OperationalError as exc:
        logger.error("Failed to purge stale leases due to database contention: %s", exc)
    finally:
        if conn:
            conn.close()

    if purged > 0:
        logger.info("Purged %d stale turn leases at ts=%.2f", purged, now)
    return purged


def _is_pid_running(pid: int) -> bool:
    if pid is None or pid <= 0:
        return False
    try:
        # Windows-friendly existence probe via tasklist.
        out = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            text=True,
            timeout=5,
            stderr=subprocess.DEVNULL,
        )
        if "No tasks" in out or not out.strip():
            return False
        return str(pid) in out
    except Exception:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
        except Exception:
            return False


def _read_pid_file(pid_path: Path) -> Optional[int]:
    if not pid_path.exists():
        return None
    try:
        raw = pid_path.read_text(encoding="utf-8").strip()
        if not raw:
            return None
        if raw.isdigit():
            return int(raw)
        data = json.loads(raw)
        pid = data.get("pid")
        return int(pid) if pid is not None else None
    except Exception as exc:
        logger.debug("Failed reading pid file %s: %s", pid_path, exc)
        return None


def get_profile_gateway_pid(profile: dict) -> Optional[int]:
    """Return live PID for one profile gateway, or None if down/stale."""
    pid = _read_pid_file(profile["pid_file"])
    if pid is not None and _is_pid_running(pid):
        return pid
    # Fallback: scan running python command lines for this profile's gateway run.
    try:
        ps = (
            "Get-CimInstance Win32_Process -Filter \"name='python.exe'\" | "
            "Where-Object { $_.CommandLine -match 'gateway run' -and $_.CommandLine -match '"
            + profile["name"]
            + "' } | Select-Object -ExpandProperty ProcessId"
        )
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps],
            text=True,
            timeout=8,
            stderr=subprocess.DEVNULL,
        ).strip()
        for line in out.splitlines():
            line = line.strip()
            if line.isdigit() and _is_pid_running(int(line)):
                return int(line)
    except Exception as exc:
        logger.debug("Process scan fallback failed for %s: %s", profile["name"], exc)
    return None


def get_gateway_pid() -> Optional[int]:
    """Compatibility: any critical profile gateway PID (prefer active CoS profile)."""
    for profile in PROFILE_GATEWAYS:
        pid = get_profile_gateway_pid(profile)
        if pid is not None:
            return pid
    return None


def get_all_gateway_status() -> Dict[str, Optional[int]]:
    return {p["name"]: get_profile_gateway_pid(p) for p in PROFILE_GATEWAYS}


def _wmi_spawn(command_line: str, current_directory: str) -> bool:
    # Escape single quotes for PowerShell single-quoted string embedding.
    cmd_escaped = command_line.replace("'", "''")
    dir_escaped = current_directory.replace("'", "''")
    ps_cmd = (
        "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments "
        f"@{{CommandLine = '{cmd_escaped}'; CurrentDirectory = '{dir_escaped}'}}"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if res.returncode != 0:
            logger.error("WMI spawn error: %s", res.stderr or res.stdout)
            return False
        return True
    except Exception as exc:
        logger.error("Failed WMI spawn: %s", exc)
        return False


def ensure_profile_gateway_running(profile: dict) -> bool:
    """Ensure one profile gateway is running; respawn via WMI + profile VBS if missing."""
    pid = get_profile_gateway_pid(profile)
    if pid is not None:
        return True

    vbs = profile["vbs"]
    if not vbs.exists():
        logger.error("Gateway VBS missing for %s at %s", profile["name"], vbs)
        return False

    logger.warning(
        "Hermes gateway profile=%s is down. Respawning via WMI + %s ...",
        profile["name"],
        vbs.name,
    )
    cmd = f'wscript.exe "{vbs}"'
    ok = _wmi_spawn(cmd, str(profile["workdir"]))
    if not ok:
        return False

    # Wait for pid file / process to appear.
    for _ in range(8):
        time.sleep(1.0)
        new_pid = get_profile_gateway_pid(profile)
        if new_pid is not None:
            logger.info(
                "Gateway profile=%s respawned successfully. New PID: %s",
                profile["name"],
                new_pid,
            )
            return True

    logger.error(
        "Gateway profile=%s respawn initiated but PID still missing after wait",
        profile["name"],
    )
    return False


def ensure_gateway_running() -> bool:
    """Ensure all critical profile gateways are running."""
    results = []
    for profile in PROFILE_GATEWAYS:
        results.append(ensure_profile_gateway_running(profile))
    return all(results)


CURSOR_API_CMD = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\node\cursor-agent-api.cmd")
SERVICES_TO_MONITOR = [
    {
        "name": "Cursor CLI Bridge",
        "port": 4646,
        "url": "http://127.0.0.1:4646/health",
        "type": "cursor_bridge",
        "critical": True,
    },
    # Port 9119 dashboard removed — no longer exists after Hermes Desktop
    # reinstall to C:\hsi21 (v2026.8.31, backend 0.21.0).
    {
        "name": "Realtor Front Door",
        "port": 8000,
        "url": "http://127.0.0.1:8000/",
        "type": "dev_launcher",
        "critical": False,
    },
    {
        "name": "Listing Intake Engine",
        "port": 8765,
        "url": "http://127.0.0.1:8765/api/listing/queue",
        "type": "dev_launcher",
        "critical": False,
    },
    {
        "name": "Discovery Brief Receiver",
        "port": 8787,
        "url": "http://127.0.0.1:8787/health",
        "type": "dev_launcher",
        "critical": False,
    },
]


def check_http_alive(url: str, timeout: float = 2.0) -> bool:
    """Returns True if the HTTP endpoint responds."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ApexGuardian/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 301, 302)
    except Exception:
        return False


def _throttled_warning(key: str, message: str, *args) -> None:
    now = time.time()
    last = _WARN_LAST.get(key, 0.0)
    if now - last >= _WARN_INTERVAL_SEC:
        logger.warning(message, *args)
        _WARN_LAST[key] = now
    else:
        logger.debug(message + " (throttled)", *args)


def ensure_cursor_bridge_running() -> bool:
    """Check port 4646 health; auto-resurrect if down."""
    if check_http_alive("http://127.0.0.1:4646/health"):
        return True

    logger.warning("⚡ [GUARDIAN] Cursor CLI Bridge (:4646) is DOWN. Auto-resurrecting...")
    if not CURSOR_API_CMD.exists():
        logger.error("cursor-agent-api.cmd not found at %s", CURSOR_API_CMD)
        return False

    cmd = f'cmd.exe /c "{CURSOR_API_CMD}" run 4646'
    ok = _wmi_spawn(cmd, str(CURSOR_API_CMD.parent))
    if not ok:
        return False
    # CLI verification can outlast a single 2.5-second startup check.
    # Poll the same child; never spawn another process during this wait.
    alive = False
    for _ in range(12):
        time.sleep(2.5)
        alive = check_http_alive("http://127.0.0.1:4646/health")
        if alive:
            break
    if alive:
        logger.info("⚡ [GUARDIAN] Cursor CLI Bridge (:4646) successfully revived.")
    else:
        logger.error("⚡ [GUARDIAN] Cursor CLI Bridge (:4646) revive failed.")
    return alive


def audit_all_services() -> dict:
    """Audits critical ports and auto-heals Cursor bridge."""
    status_report = {}

    cursor_ok = ensure_cursor_bridge_running()
    status_report["cursor_bridge_4646"] = cursor_ok

    for svc in SERVICES_TO_MONITOR:
        if svc["type"] == "cursor_bridge":
            continue
        alive = check_http_alive(svc["url"])
        status_report[f"{svc['name']}_:{svc['port']}"] = alive
        if not alive:
            key = f"{svc['name']}:{svc['port']}"
            if svc.get("critical", False):
                logger.warning("Service %s on port %d is unresponsive!", svc["name"], svc["port"])
            else:
                _throttled_warning(
                    key,
                    "Service %s on port %d is unresponsive (non-critical)",
                    svc["name"],
                    svc["port"],
                )

    return status_report


def run_guardian_cycle(db_path: Path = DEFAULT_STATE_DB) -> dict:
    """Run one single audit, auto-heal & repair cycle."""
    purged = purge_stale_leases(db_path=db_path)
    before = get_all_gateway_status()
    restarted_any = False
    if any(pid is None for pid in before.values()):
        restarted_any = ensure_gateway_running()
    after = get_all_gateway_status()
    services_status = audit_all_services()

    return {
        "timestamp": time.time(),
        "leases_purged": purged,
        "gateway_running": all(pid is not None for pid in after.values()),
        "gateway_pids": after,
        "gateway_pid": after.get(PRIMARY_COS_PROFILE) or next((p for p in after.values() if p), None),
        "gateway_restarted": restarted_any,
        "services": services_status,
    }


def _release_lock() -> None:
    try:
        if LOCK_PATH.exists():
            data = LOCK_PATH.read_text(encoding="utf-8").strip()
            if data.startswith(str(os.getpid())):
                LOCK_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def acquire_singleton_or_exit() -> None:
    """Ensure only one guardian daemon runs."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        try:
            old_raw = LOCK_PATH.read_text(encoding="utf-8").strip().split()[0]
            old_pid = int(old_raw)
            if old_pid != os.getpid() and _is_pid_running(old_pid):
                logger.error(
                    "Another lease_guardian holds the lock (PID %s). Exiting duplicate.",
                    old_pid,
                )
                sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            pass
    LOCK_PATH.write_text(f"{os.getpid()} {time.time():.0f}\n", encoding="utf-8")
    atexit.register(_release_lock)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hermes SQLite Lease Guardian & Watchdog")
    parser.add_argument("--daemon", action="store_true", help="Run continuously every 60s")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Take over singleton lock even if another PID is recorded (does not kill it)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(LOG_PATH), encoding="utf-8"),
        ],
    )

    if args.daemon:
        if args.force and LOCK_PATH.exists():
            try:
                LOCK_PATH.unlink()
            except Exception:
                pass
        acquire_singleton_or_exit()
        logger.info(
            "Starting Lease Guardian daemon loop (interval=%ds, pid=%s)...",
            args.interval,
            os.getpid(),
        )
        while True:
            try:
                result = run_guardian_cycle()
                logger.info(
                    "cycle ok gateways=%s cursor=%s",
                    result.get("gateway_pids"),
                    result.get("services", {}).get("cursor_bridge_4646"),
                )
            except Exception as exc:
                logger.error("Error during guardian cycle: %s", exc)
            time.sleep(args.interval)
    else:
        result = run_guardian_cycle()
        print("Guardian cycle completed:", result)
