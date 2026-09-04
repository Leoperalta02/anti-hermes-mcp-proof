"""
Apex Luxury AI — Operator Gate Registry
Canonical evidence-backed gate state (SOP §6.5). Env vars override for local dev;
evidence/operator_gates.json is the durable record when Leo lifts gates.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GATES_FILE = WORKSPACE_ROOT / "evidence" / "operator_gates.json"


def gates_file_path() -> Path:
    override = os.getenv("APEX_OPERATOR_GATES_FILE", "").strip()
    return Path(override) if override else DEFAULT_GATES_FILE

DEFAULT_GATES: Dict[str, bool] = {
    "a4_watch_complete": False,
    "live_provision_enabled": False,
    "telegram_live_enabled": False,
    "alienware_hq_hold_active": True,
}

ENV_GATE_MAP = {
    "a4_watch_complete": "APEX_A4_WATCH_COMPLETE",
    "live_provision_enabled": "APEX_LIVE_PROVISION_ENABLED",
    "telegram_live_enabled": "APEX_TELEGRAM_LIVE",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def load_operator_gates() -> Dict[str, Any]:
    gates_file = gates_file_path()
    if not gates_file.exists():
        return {
            "version": 1,
            "gates": dict(DEFAULT_GATES),
            "history": [],
        }
    try:
        return json.loads(gates_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "version": 1,
            "gates": dict(DEFAULT_GATES),
            "history": [],
        }


def save_operator_gates(payload: Dict[str, Any]) -> Path:
    gates_file = gates_file_path()
    gates_file.parent.mkdir(parents=True, exist_ok=True)
    gates_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return gates_file


def is_gate_open(gate_name: str) -> bool:
    """Return True when gate is open. Env var wins over evidence file."""
    env_name = ENV_GATE_MAP.get(gate_name)
    if env_name and _truthy_env(env_name):
        return True

    data = load_operator_gates()
    gates = data.get("gates") if isinstance(data.get("gates"), dict) else {}

    if gate_name == "alienware_hq_hold_active":
        # HOLD active means gate closed for HQ hops
        if _truthy_env("APEX_ALIENWARE_HQ_HOLD"):
            return True
        if env_name and _truthy_env(env_name):
            return True
        return bool(gates.get("alienware_hq_hold_active", True))

    return bool(gates.get(gate_name, DEFAULT_GATES.get(gate_name, False)))


def is_a4_watch_complete() -> bool:
    return is_gate_open("a4_watch_complete")


def is_live_provision_enabled() -> bool:
    return is_gate_open("live_provision_enabled") and is_a4_watch_complete()


def is_telegram_live_enabled() -> bool:
    return is_gate_open("telegram_live_enabled")


def is_alienware_hq_hold_active() -> bool:
    return is_gate_open("alienware_hq_hold_active")


def record_gate_lift(
    *,
    recorded_by: str = "Leo Peralta",
    notes: str = "",
    a4_watch_complete: Optional[bool] = None,
    live_provision_enabled: Optional[bool] = None,
    telegram_live_enabled: Optional[bool] = None,
    alienware_hq_hold_active: Optional[bool] = None,
) -> Dict[str, Any]:
    """Record operator gate lift in evidence/operator_gates.json."""
    data = load_operator_gates()
    gates = dict(DEFAULT_GATES)
    gates.update(data.get("gates") if isinstance(data.get("gates"), dict) else {})

    updates: Dict[str, bool] = {}
    if a4_watch_complete is not None:
        updates["a4_watch_complete"] = a4_watch_complete
    if live_provision_enabled is not None:
        updates["live_provision_enabled"] = live_provision_enabled
    if telegram_live_enabled is not None:
        updates["telegram_live_enabled"] = telegram_live_enabled
    if alienware_hq_hold_active is not None:
        updates["alienware_hq_hold_active"] = alienware_hq_hold_active

    gates.update(updates)
    entry = {
        "timestamp": utc_now_iso(),
        "recorded_by": recorded_by,
        "notes": notes,
        "updates": updates,
    }
    history = data.get("history") if isinstance(data.get("history"), list) else []
    history.append(entry)

    payload = {
        "version": 1,
        "last_updated": utc_now_iso(),
        "recorded_by": recorded_by,
        "gates": gates,
        "history": history[-50:],
    }
    save_operator_gates(payload)
    return payload


def lift_provision_gates(
    recorded_by: str = "Leo Peralta",
    notes: str = "Leo lifted A4 + live provision gate",
) -> Dict[str, Any]:
    """Lift A4 watch and live provision gates (standard Leo approval flow)."""
    return record_gate_lift(
        recorded_by=recorded_by,
        notes=notes,
        a4_watch_complete=True,
        live_provision_enabled=True,
    )


def lift_all_operator_gates(
    recorded_by: str = "Leo Peralta",
    notes: str = "Leo lifted operator gates",
    *,
    include_telegram: bool = True,
    lift_hq_hold: bool = False,
) -> Dict[str, Any]:
    return record_gate_lift(
        recorded_by=recorded_by,
        notes=notes,
        a4_watch_complete=True,
        live_provision_enabled=True,
        telegram_live_enabled=True if include_telegram else None,
        alienware_hq_hold_active=False if lift_hq_hold else None,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Record or inspect Apex operator gates")
    sub = parser.add_subparsers(dest="cmd")

    show = sub.add_parser("show", help="Print current gate state")
    show.set_defaults(cmd="show")

    lift = sub.add_parser("lift", help="Record gate lift in evidence")
    lift.add_argument(
        "scope",
        choices=["provision", "telegram", "all"],
        help="Which gates to lift",
    )
    lift.add_argument("--by", default="Leo Peralta")
    lift.add_argument("--notes", default="")
    lift.add_argument("--lift-hq-hold", action="store_true")

    args = parser.parse_args()

    if args.cmd == "show":
        data = load_operator_gates()
        print(json.dumps(data, indent=2))
        return

    if args.cmd == "lift":
        if args.scope == "provision":
            result = lift_provision_gates(recorded_by=args.by, notes=args.notes or "Provision gate lifted")
        elif args.scope == "telegram":
            result = record_gate_lift(
                recorded_by=args.by,
                notes=args.notes or "Telegram live gate lifted",
                telegram_live_enabled=True,
            )
        else:
            result = lift_all_operator_gates(
                recorded_by=args.by,
                notes=args.notes or "Operator gates lifted",
                include_telegram=True,
                lift_hq_hold=args.lift_hq_hold,
            )
        print(json.dumps(result, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
