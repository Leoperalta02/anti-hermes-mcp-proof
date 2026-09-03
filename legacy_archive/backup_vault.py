#!/usr/bin/env python3
"""
backup_vault.py: Safely extracts all OAuth tokens, API secrets, playbooks, and configuration
from local workspace and remote VPS into a persistent vault_backup directory.
"""

import json
import os
import shutil
import paramiko
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()
BACKUP_DIR = WORKSPACE_ROOT / "vault_backup"

VPS_HOST = '159.223.183.138'
VPS_PORT = 22
VPS_USER = 'root'
VPS_PASS = '25021121Wow'

def create_backup():
    print("=== STARTING SAFE VAULT BACKUP ===")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    # 1. Local Playbooks & Blueprints
    files_to_copy = [
        "NIKKI_CONVERSION_PLAYBOOK.md",
        "PROJECT_BLUEPRINT_AI_HIGHLEVEL.md",
        "PROJECT_BLUEPRINT_NETWORK_SECURITY_MSP.md",
        "SECURITY_MODEL.md",
        "gpu_bridge.py"
    ]

    for fname in files_to_copy:
        src = WORKSPACE_ROOT / fname
        if src.exists():
            dest = BACKUP_DIR / fname
            shutil.copy2(src, dest)
            manifest.append({"type": "local_file", "name": fname, "size": src.stat().st_size})
            print(f"[+] Saved local asset: {fname}")

    # 2. Remote VPS Secrets & OAuth Tokens
    print(f"Connecting to VPS {VPS_HOST} to harvest OAuth & Vault secrets...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASS, timeout=10)
        sftp = ssh.open_sftp()

        remote_secrets = [
            "/opt/leo-os-office/data/vault_secrets.json",
            "/opt/leo-os-office/data/google_oauth_token.json",
            "/opt/leo-os-office/data/custom_fleet.json"
        ]

        for rpath in remote_secrets:
            rname = os.path.basename(rpath)
            dest = BACKUP_DIR / rname
            try:
                sftp.get(rpath, str(dest))
                manifest.append({"type": "remote_secret", "name": rname, "size": dest.stat().st_size})
                print(f"[+] Harvested remote secret: {rname}")
            except Exception as e:
                print(f"[-] Notice for {rname}: {e}")

        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"[-] VPS SSH Connection notice: {e}")

    manifest_file = BACKUP_DIR / "backup_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"=== SAFE BACKUP COMPLETED: {len(manifest)} ASSETS SECURED IN {BACKUP_DIR} ===")
    return manifest

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    create_backup()
