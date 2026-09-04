#!/usr/bin/env python3
"""
Apex Sovereign Realtor OS — Unified CLI

One entry point for Leo/Cursor/Anti. Safe on cloud VM or Alienware:
  python -m apex_core.apex_cli status
  python -m apex_core.apex_cli dev
  python -m apex_core.apex_cli brief provision
  python -m apex_core.apex_cli gates show
  python -m apex_core.apex_cli host

Cloud VM: code, tests, gates, dry-run (evidence paths).
Alienware: everything above + governance patch, live provision dirs, gateway.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

ALIENWARE_REPO = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof")
ALIENWARE_HERMES_AGENT = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-agent")
ALIENWARE_BRIEFS = Path(r"C:\LEO-LAB-ANTIGRAVITY\business-scope\onboarding-briefs")


def detect_host() -> Dict[str, Any]:
    on_alienware = ALIENWARE_REPO.exists() or os.name == "nt" and "LEO-LAB" in os.getenv("USERPROFILE", "")
    hermes_agent = ALIENWARE_HERMES_AGENT.exists()
    briefs_dir = ALIENWARE_BRIEFS if ALIENWARE_BRIEFS.exists() else None
    return {
        "host_label": "alienware" if on_alienware and ALIENWARE_REPO.exists() else "cloud_or_other",
        "workspace": str(WORKSPACE_ROOT),
        "alienware_repo_exists": ALIENWARE_REPO.exists(),
        "hermes_agent_exists": hermes_agent,
        "briefs_dir": str(briefs_dir) if briefs_dir else None,
        "can_patch_governance": ALIENWARE_HERMES_AGENT.parent.exists(),
        "can_live_provision": bool(briefs_dir),
    }


def cmd_host(_args: argparse.Namespace) -> int:
    info = detect_host()
    print(json.dumps(info, indent=2))
    if info["host_label"] == "cloud_or_other":
        print("\nNote: Cloud VM cannot reach Alienware gateway, Telegram bot env, or C:\\ paths.")
        print("Run host-only commands on Alienware: gates ok, dev, brief — governance patch needs Alienware.")
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    from apex_core.operator_gates import load_operator_gates
    from apex_core.provision_gate import evaluate_provision_gate

    host = detect_host()
    gates = load_operator_gates()
    live_gate = evaluate_provision_gate("APPROVE PROVISION")

    print("=" * 56)
    print("  Apex CLI — Status")
    print("=" * 56)
    print(f"  Host:     {host['host_label']}")
    print(f"  Workspace: {host['workspace']}")
    print(f"  Live APPROVE PROVISION: {'OPEN' if live_gate['provision_allowed'] else 'BLOCKED'}")
    print(f"  Gate mode: {live_gate['gate_mode']}")
    print(f"  HQ HOLD (evidence): {gates.get('gates', {}).get('alienware_hq_hold_active', True)}")
    print(f"  Telegram live gate: {gates.get('gates', {}).get('telegram_live_enabled', False)}")
    print(f"  Bot token set: {bool(os.getenv('APEX_TELEGRAM_BOT_TOKEN'))}")
    print("  §12: STAGED ONLY until deploy/host/MLS verified")
    print("=" * 56)
    return 0


def cmd_gates(args: argparse.Namespace) -> int:
    from apex_core.operator_gates import (
        lift_all_operator_gates,
        lift_provision_gates,
        load_operator_gates,
        record_gate_lift,
    )

    if args.gates_cmd == "show":
        print(json.dumps(load_operator_gates(), indent=2))
        return 0

    if args.gates_cmd == "lift":
        if args.scope == "provision":
            result = lift_provision_gates(recorded_by=args.by, notes=args.notes or "CLI lift provision")
        elif args.scope == "telegram":
            result = record_gate_lift(
                recorded_by=args.by,
                notes=args.notes or "CLI lift telegram",
                telegram_live_enabled=True,
            )
        else:
            result = lift_all_operator_gates(
                recorded_by=args.by,
                notes=args.notes or "CLI lift all",
                include_telegram=True,
                lift_hq_hold=args.lift_hq_hold,
            )
        print(json.dumps(result, indent=2))
        return 0

    return 1


def cmd_brief(args: argparse.Namespace) -> int:
    from apex_core.brief_watcher import BriefWatcher, resolve_briefs_dir

    briefs_dir = Path(args.dir) if args.dir else resolve_briefs_dir()
    watcher = BriefWatcher(briefs_dir=briefs_dir)

    if args.brief_cmd == "triage":
        results = watcher.scan_once()
        print(f"Triaged {len(results)} brief(s).")
        if results:
            print(json.dumps(results, indent=2))
        return 0

    if args.brief_cmd == "provision":
        results = watcher.scan_provision_ready()
        print(f"Provision scan: {len(results)} brief(s).")
        if results:
            print(json.dumps(results, indent=2))
        return 0

    return 1


def cmd_dev(_args: argparse.Namespace) -> int:
    from apex_core.dev_launcher import main as dev_main

    dev_main()
    return 0


def cmd_dryrun(_args: argparse.Namespace) -> int:
    from apex_core.execute_dryrun_lead import run_dryrun_lead

    result = run_dryrun_lead()
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "PASS" else 1


def cmd_governance(_args: argparse.Namespace) -> int:
    host = detect_host()
    script = WORKSPACE_ROOT / "update_managed_agent_tool_governance.py"
    if not script.exists():
        print("Governance script not found.", file=sys.stderr)
        return 1
    if not host["can_patch_governance"]:
        print("Blocked: not on Alienware — cannot write hermes-agent/tools/managed_agent_tool.py", file=sys.stderr)
        print("Run on Alienware: python -m apex_core.apex_cli governance", file=sys.stderr)
        return 2
    subprocess.run([sys.executable, str(script)], check=False)
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    if args.verbose:
        cmd.append("-v")
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apex",
        description="Apex Sovereign Realtor OS — unified CLI (cloud + Alienware)",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("host", help="Show host capabilities (cloud vs Alienware)")
    sub.add_parser("status", help="Gates, provision state, §12 posture")
    sub.add_parser("dev", help="Start unified dev stack (preview, intake, brief)")
    sub.add_parser("dryrun", help="Run §9 dry-run lead executor")

    g = sub.add_parser("gates", help="Operator gate registry")
    g_sub = g.add_subparsers(dest="gates_cmd")
    g_sub.add_parser("show")
    gl = g_sub.add_parser("lift")
    gl.add_argument("scope", choices=["provision", "telegram", "all"])
    gl.add_argument("--by", default="Leo Peralta")
    gl.add_argument("--notes", default="")
    gl.add_argument("--lift-hq-hold", action="store_true")

    b = sub.add_parser("brief", help="Brief watcher / provision")
    b_sub = b.add_subparsers(dest="brief_cmd")
    b_sub.add_parser("triage", help="Scan and triage new briefs once")
    bp = b_sub.add_parser("provision", help="Provision approved briefs")
    b.add_argument("--dir", default="", help="Override onboarding-briefs directory")

    sub.add_parser("governance", help="Patch managed_agent_tool on Alienware only")

    t = sub.add_parser("test", help="Run unittest discover -s tests")
    t.add_argument("-v", "--verbose", action="store_true")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "host": cmd_host,
        "status": cmd_status,
        "dev": cmd_dev,
        "dryrun": cmd_dryrun,
        "gates": cmd_gates,
        "brief": cmd_brief,
        "governance": cmd_governance,
        "test": cmd_test,
    }

    if not args.command:
        parser.print_help()
        return 0

    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
