"""
Apex Luxury AI — Hermes Brief Watcher & Triage Alert Hook (W1 & W2)
Monitors onboarding briefs directory, validates intake payloads, executes Hermes triage (§6 SOP),
and stages structured Telegram alerts for Leo Peralta (§12 SOP compliant — zero false claims).
"""

import os
import sys
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure clean UTF-8 console output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BRIEFS_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\business-scope\onboarding-briefs")
_WORKSPACE_BRIEFS_FALLBACK = WORKSPACE_ROOT / "evidence" / "onboarding-briefs"
EVIDENCE_DIR = WORKSPACE_ROOT / "evidence"
PROCESSED_FILE = EVIDENCE_DIR / "processed_briefs.json"
ALERT_FILE = EVIDENCE_DIR / "brief_telegram_alert.json"
TRIAGE_LOG = EVIDENCE_DIR / "brief_triage_log.jsonl"

SECRET_RE = re.compile(
    r"(password|passwd|api[_-]?key|secret|token|bearer|authorization|"
    r"connection string|private[_-]?key)",
    re.IGNORECASE,
)

DEFAULT_TELEGRAM_TARGET = "telegram:8349762599"
TELEGRAM_TARGET = os.getenv("APEX_TELEGRAM_TARGET", DEFAULT_TELEGRAM_TARGET)


def resolve_briefs_dir() -> Path:
    env = os.getenv("APEX_BRIEFS_DIR")
    if env:
        return Path(env)
    if DEFAULT_BRIEFS_DIR.parent.exists():
        return DEFAULT_BRIEFS_DIR
    return _WORKSPACE_BRIEFS_FALLBACK


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BriefWatcher:
    def __init__(
        self,
        briefs_dir: Optional[Path] = None,
        evidence_dir: Optional[Path] = None,
        telegram_target: Optional[str] = None,
    ):
        self.briefs_dir = Path(briefs_dir) if briefs_dir else resolve_briefs_dir()
        self.evidence_dir = Path(evidence_dir) if evidence_dir else EVIDENCE_DIR
        self.telegram_target = telegram_target or os.getenv("APEX_TELEGRAM_TARGET", TELEGRAM_TARGET)
        self.processed_file = self.evidence_dir / "processed_briefs.json"
        self.alert_file = self.evidence_dir / "brief_telegram_alert.json"
        self.triage_log = self.evidence_dir / "brief_triage_log.jsonl"
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.briefs_dir.mkdir(parents=True, exist_ok=True)

    def load_processed_ids(self) -> set:
        if self.processed_file.exists():
            try:
                with open(self.processed_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return set(data)
            except Exception as e:
                print(f"[BriefWatcher] Warning reading processed file: {e}")
        return set()

    def mark_processed(self, stem: str):
        processed = self.load_processed_ids()
        processed.add(stem)
        with open(self.processed_file, "w", encoding="utf-8") as f:
            json.dump(sorted(list(processed)), f, indent=2)

    def triage_brief(self, brief_path: Path) -> Dict[str, Any]:
        """
        Executes Hermes triage (§6 of ROSIE_ONBOARDING_SOP.md):
        1. Acknowledge brief
        2. Validate (no credentials, required fields)
        3. Classify (STAGE:READY vs STAGE:DISCOVERY vs STAGE:DEFER vs STAGE:REJECTED_CREDENTIALS)
        4. Surface structured alert to Leo (Telegram target, zero false claims)
        5. Log event
        """
        stem = brief_path.stem

        try:
            with open(brief_path, "r", encoding="utf-8") as f:
                brief = json.load(f)
        except Exception as e:
            return {
                "stem": stem,
                "status": "ERROR",
                "error": f"Failed to parse JSON: {e}"
            }

        brief_str = json.dumps(brief)

        # 1. Credentials Check (§6.2)
        if SECRET_RE.search(brief_str):
            classification = "STAGE:REJECTED_CREDENTIALS"
            alert_msg = (
                f"🚨 [HERMES TRIAGE: CREDENTIALS REJECTED]\n\n"
                f"📋 Brief ID: {stem}\n"
                f"⚠️ Security Alert: Brief payload contained suspected passwords, API keys, or tokens.\n"
                f"🛡️ Action: Rejected per security policy. Do not provision.\n"
                f"📁 Artifact: {brief_path.name}"
            )
            stage_valid = False
        else:
            # 2. Validation & Classification (§6.2 & §6.3)
            answers = brief.get("answers") if isinstance(brief.get("answers"), dict) else {}
            name = answers.get("full_name") or brief.get("name") or "profile_unknown"
            brokerage = answers.get("brokerage") or "brokerage_unknown"
            market = answers.get("market") or "market_unknown"
            needs = answers.get("needs") or []
            if isinstance(needs, list) and needs:
                needs_str = ", ".join(str(n) for n in needs)
            else:
                needs_str = "needs_unknown"

            has_name = name not in ("profile_unknown", "", None)
            has_needs = needs_str != "needs_unknown"

            is_deferred = (
                brief.get("leo_decision") == "DEFER"
                or brief.get("hermes_stage") == "STAGE:DEFER"
                or answers.get("defer") is True
                or brief.get("defer") is True
            )

            if is_deferred:
                classification = "STAGE:DEFER"
                action_recommendation = "Brief is deferred per operator instruction. Awaiting Leo re-activation."
            elif has_name and has_needs:
                classification = "STAGE:READY"
                action_recommendation = "Review brief and await Leo gate ('APPROVE PROVISION DRYRUN')."
            else:
                classification = "STAGE:DISCOVERY"
                action_recommendation = "Incomplete discovery brief. Follow up on required intake fields."

            team_info = ""
            team_name = answers.get("team_name")
            team_leader = answers.get("team_leader")
            if team_name or team_leader:
                t_parts = []
                if team_name:
                    t_parts.append(f"Team: {team_name}")
                if team_leader:
                    t_parts.append(f"Mentor: {team_leader}")
                team_info = f"👥 Organization: {' · '.join(t_parts)}\n"

            # 3. Alert Formatting (§12 & §6.4 — ZERO FALSE CLAIMS)
            alert_msg = (
                f"📥 [HERMES TRIAGE: NEW ONBOARDING BRIEF]\n\n"
                f"📋 Brief ID: {stem}\n"
                f"👤 Realtor: {name}\n"
                f"🏢 Brokerage: {brokerage}\n"
                f"{team_info}"
                f"📍 Market: {market}\n"
                f"🎯 Needs: {needs_str}\n"
                f"🏷️ Triage Tag: {classification}\n\n"
                f"🛡️ Posture (§12 SOP): STAGED ONLY\n"
                f"• Agent deployed: NO\n"
                f"• Public portal live: NO\n"
                f"• MLS connected: NO\n\n"
                f"👉 Recommended Action: {action_recommendation}"
            )
            stage_valid = True

        # 4. Stage Hermes Telegram Alert
        alert_payload = {
            "channel": self.telegram_target,
            "brief_id": stem,
            "brief_file": str(brief_path),
            "timestamp": utc_now_iso(),
            "classification": classification,
            "claims": {
                "agent_deployed": False,
                "portal_created": False,
                "mls_connected": False,
                "voice_enabled": False,
                "calendar_synced": False
            },
            "message": alert_msg
        }

        with open(self.alert_file, "w", encoding="utf-8") as f:
            json.dump(alert_payload, f, indent=2)

        # 4b. Gated Telegram dispatch (staged by default; live only if APEX_TELEGRAM_LIVE=1)
        from apex_core.telegram_dispatch import dispatch_telegram_alert

        dispatch_result = dispatch_telegram_alert(alert_payload, evidence_dir=self.evidence_dir)
        alert_payload["dispatch"] = dispatch_result

        # 5. Append to triage log
        with open(self.triage_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert_payload) + "\n")

        # 6. Update brief file with triage metadata if valid
        if stage_valid:
            brief["hermes_triage_at"] = utc_now_iso()
            brief["hermes_stage"] = classification
            brief["hermes_alert_staged"] = True
            try:
                with open(brief_path, "w", encoding="utf-8") as f:
                    json.dump(brief, f, indent=2)
            except Exception as e:
                print(f"[BriefWatcher] Warning updating brief metadata: {e}")

        # Mark processed
        self.mark_processed(stem)
        print(f"[Hermes Triage] Processed brief {stem} -> {classification}")

        return alert_payload

    def scan_once(self) -> List[Dict[str, Any]]:
        """Scans briefs directory for any unprocessed JSON files."""
        if not self.briefs_dir.exists():
            return []

        processed = self.load_processed_ids()
        results = []

        json_files = sorted(list(self.briefs_dir.glob("*.json")))
        for p in json_files:
            if p.stem in processed:
                continue

            # Check if brief was already triaged internally
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("hermes_triage_at"):
                        self.mark_processed(p.stem)
                        continue
            except Exception:
                pass

            res = self.triage_brief(p)
            results.append(res)

        return results

    def watch_loop(self, poll_interval: float = 3.0, max_iterations: Optional[int] = None):
        """Continuously watches for new briefs until interrupted."""
        print(f"[BriefWatcher] Watching {self.briefs_dir} (polling every {poll_interval}s)...")
        iterations = 0
        try:
            while True:
                results = self.scan_once()
                if results:
                    print(f"[BriefWatcher] Triaged {len(results)} new brief(s)")
                iterations += 1
                if max_iterations and iterations >= max_iterations:
                    break
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\n[BriefWatcher] Watcher stopped.")


brief_watcher = BriefWatcher()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hermes Brief Watcher & Triage (W1 & W2)")
    parser.add_argument("--once", action="store_true", help="Run a single scan and exit")
    parser.add_argument("--dir", type=str, default=None, help="Custom briefs directory path")
    args = parser.parse_args()

    custom_dir = Path(args.dir) if args.dir else None
    watcher = BriefWatcher(briefs_dir=custom_dir)

    if args.once:
        found = watcher.scan_once()
        print(f"Completed scan. Triaged {len(found)} brief(s).")
    else:
        watcher.watch_loop()
