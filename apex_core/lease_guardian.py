"""SQLite Lease Guardian & Gateway Watchdog for Hermes State.

Ensures:
1. SQLite single-writer discipline by auto-purging expired session turn leases.
2. Hermes Gateway process liveness (checks authoritative get_running_pid, respawns via WMI if dropped).
3. Zero lingering handles on state.db.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("lease_guardian")

DEFAULT_HERMES_HOME = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state")
DEFAULT_STATE_DB = DEFAULT_HERMES_HOME / "state.db"
GATEWAY_VBS = DEFAULT_HERMES_HOME / "gateway-service" / "Hermes_Gateway.vbs"
HERMES_AGENT_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-agent")
HERMES_PYTHON = DEFAULT_HERMES_HOME / "hermes-agent" / "venv" / "Scripts" / "python.exe"

# Ensure HERMES_HOME is always configured
os.environ.setdefault("HERMES_HOME", str(DEFAULT_HERMES_HOME))


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
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='session_turn_leases';")
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


def get_gateway_pid() -> Optional[int]:
    """Authoritative check for live gateway process via Hermes status machinery or subprocess."""
    # First attempt direct import if running under the Hermes venv
    try:
        if str(HERMES_AGENT_ROOT) not in sys.path:
            sys.path.insert(0, str(HERMES_AGENT_ROOT))
        from gateway.status import get_running_pid  # type: ignore
        return get_running_pid()
    except Exception:
        pass

    # Fallback to querying via the hermes venv interpreter
    if HERMES_PYTHON.exists():
        try:
            cmd = [
                str(HERMES_PYTHON),
                "-c",
                (
                    "import os, sys; os.environ['HERMES_HOME'] = r'C:\\LEO-LAB-ANTIGRAVITY\\hermes-state'; "
                    "sys.path.insert(0, r'C:\\LEO-LAB-ANTIGRAVITY\\hermes-agent'); "
                    "from gateway.status import get_running_pid; "
                    "pid = get_running_pid(); "
                    "print(pid if pid is not None else '')"
                ),
            ]
            out = subprocess.check_output(cmd, text=True, timeout=5).strip()
            if out and out.isdigit():
                return int(out)
        except Exception as exc:
            logger.debug("Failed to query gateway PID via hermes python: %s", exc)

    return None


def ensure_gateway_running() -> bool:
    """Ensure Hermes gateway is running; respawn via WMI if missing."""
    pid = get_gateway_pid()
    if pid is not None:
        return True

    if not GATEWAY_VBS.exists():
        logger.error("Gateway launcher script not found at %s", GATEWAY_VBS)
        return False

    logger.warning("Hermes gateway is down. Respawning via WMI...")
    ps_cmd = (
        "Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments "
        "@{CommandLine = 'wscript.exe C:\\LEO-LAB-ANTIGRAVITY\\hermes-state\\gateway-service\\Hermes_Gateway.vbs'; "
        "CurrentDirectory = 'C:\\LEO-LAB-ANTIGRAVITY\\hermes-state'}"
    )
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0:
            time.sleep(2.5)
            new_pid = get_gateway_pid()
            logger.info("Gateway respawn initiated successfully. New PID: %s", new_pid)
            return new_pid is not None
        else:
            logger.error("WMI spawn returned error: %s", res.stderr)
    except Exception as exc:
        logger.error("Failed to invoke WMI process spawn: %s", exc)

    return False


def run_guardian_cycle(db_path: Path = DEFAULT_STATE_DB) -> dict:
    """Run one single audit & repair cycle."""
    purged = purge_stale_leases(db_path=db_path)
    current_pid = get_gateway_pid()
    restarted = False
    if current_pid is None:
        restarted = ensure_gateway_running()
        current_pid = get_gateway_pid()

    return {
        "timestamp": time.time(),
        "leases_purged": purged,
        "gateway_running": current_pid is not None,
        "gateway_pid": current_pid,
        "gateway_restarted": restarted,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hermes SQLite Lease Guardian & Watchdog")
    parser.add_argument("--daemon", action="store_true", help="Run continuously every 60s")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\evidence\guardian.log", encoding="utf-8")
        ]
    )

    if args.daemon:
        logger.info("Starting Lease Guardian daemon loop (interval=%ds)...", args.interval)
        while True:
            try:
                run_guardian_cycle()
            except Exception as exc:
                logger.error("Error during guardian cycle: %s", exc)
            time.sleep(args.interval)
    else:
        result = run_guardian_cycle()
        print("Guardian cycle completed:", result)

