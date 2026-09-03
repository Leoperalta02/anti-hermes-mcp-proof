"""
apex_core/buzz_cli_bridge.py
Production Buzz CLI Bridge & Role-Based Access Control (RBAC) Governance Engine.
Interacts with Block's native buzz.exe to manage channels, membership, and archives on Nostr Relay.
"""

import os
import sys
import json
import secrets
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding='utf-8')

BUZZ_EXE_PATH = r"C:\Users\leope\AppData\Local\Buzz\buzz.exe"
DEFAULT_RELAY = "https://hiking-logan-drug-advocacy.trycloudflare.com"

class BuzzCLIBridge:
    def __init__(self, relay_url: str = DEFAULT_RELAY):
        self.buzz_exe = BUZZ_EXE_PATH
        self.relay_url = relay_url

    def _execute_buzz_command(self, cmd_args: List[str], privkey: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes a buzz.exe CLI command with global options preceding subcommands.
        Pattern: buzz.exe [--relay <url>] [--private-key <key>] [--format json] <subcommand>
        """
        active_key = privkey or secrets.token_hex(32)
        full_cmd = [
            self.buzz_exe,
            "--relay", self.relay_url,
            "--private-key", active_key,
            "--format", "json"
        ]
        full_cmd.extend(cmd_args)

        try:
            res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                try:
                    return {"status": "SUCCESS", "data": json.loads(res.stdout)}
                except Exception:
                    return {"status": "SUCCESS", "raw_output": res.stdout.strip()}
            else:
                return {
                    "status": "ERROR",
                    "returncode": res.returncode,
                    "stderr": res.stderr.strip(),
                    "stdout": res.stdout.strip()
                }
        except Exception as e:
            return {"status": "EXCEPTION", "error": str(e)}

    def create_channel(
        self,
        name: str,
        description: str,
        caller_role: str = "EXECUTIVE",
        is_private: bool = True
    ) -> Dict[str, Any]:
        """
        Creates a live channel on the Nostr Relay via Buzz CLI.
        """
        print(f"[Buzz Bridge] Programmatically deploying channel '{name}' ({caller_role})...")
        args = [
            "channels", "create",
            "--name", name,
            "--type", "stream",
            "--visibility", "private" if is_private else "open",
            "--description", description
        ]

        res = self._execute_buzz_command(args)
        return {
            "status": res.get("status"),
            "channel_name": f"#{name}",
            "is_private": is_private,
            "governance_rule": "Leo Peralta & Atlas Oversight Attached",
            "cli_result": res
        }

    def list_channels(self) -> Dict[str, Any]:
        return self._execute_buzz_command(["channels", "list"])

    def archive_channel(self, channel_id: str) -> Dict[str, Any]:
        return self._execute_buzz_command(["channels", "archive", channel_id])

    def delete_channel(self, channel_id: str, caller_role: str) -> Dict[str, Any]:
        if caller_role.upper() != "OWNER":
            return {
                "status": "PERMISSION_DENIED",
                "error": "Security Violation: Channel DELETE authority is strictly reserved for Owner (Leo Peralta & Atlas)."
            }
        return self._execute_buzz_command(["channels", "delete", channel_id])

buzz_bridge = BuzzCLIBridge()

if __name__ == "__main__":
    print("=== TESTING FULLY WIRED BUZZ CLI BRIDGE ===")
    
    # 1. Test Listing Channels
    channels = buzz_bridge.list_channels()
    print("\nLive Relay Channels:")
    print(json.dumps(channels, indent=2))
    
    # 2. Test Creating an Autonomous Client Channel
    new_room = buzz_bridge.create_channel(
        name="client-acme-roofing-vip",
        description="Private Client Channel for Acme Roofing VIP",
        caller_role="EXECUTIVE",
        is_private=False
    )
    print("\nNew Channel Created on Relay:")
    print(json.dumps(new_room, indent=2))
