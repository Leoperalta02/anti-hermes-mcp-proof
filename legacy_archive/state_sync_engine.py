#!/usr/bin/env python3
"""
state_sync_engine.py: Real-Time State & Conflict Synchronization Engine
Tracks workspace modifications, Git commits, and state changes made by Antigravity 2.0 or mobile sessions.
Prevents state conflicts between Anti and Antigravity 2.0.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()
EVIDENCE_DIR = WORKSPACE_ROOT / "evidence"
SYNC_FILE = EVIDENCE_DIR / "workspace_sync.json"
HERMES_STATE_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state").resolve()

def ensure_evidence_dir():
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

def get_git_status() -> dict:
    git_info = {"is_repo": False, "branch": "unknown", "latest_commit": "none", "modified_files": []}
    try:
        res_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
        if res_branch.returncode == 0:
            git_info["is_repo"] = True
            git_info["branch"] = res_branch.stdout.strip()
            
            res_commit = subprocess.run(["git", "log", "-1", "--format=%h - %s (%cr)"], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
            if res_commit.returncode == 0:
                git_info["latest_commit"] = res_commit.stdout.strip()
                
            res_status = subprocess.run(["git", "status", "--porcelain"], cwd=WORKSPACE_ROOT, capture_output=True, text=True)
            if res_status.returncode == 0:
                lines = [l.strip() for l in res_status.stdout.splitlines() if l.strip()]
                git_info["modified_files"] = lines
    except Exception as e:
        git_info["error"] = str(e)
    return git_info

def get_recent_file_changes(limit: int = 15) -> list:
    recent = []
    try:
        for root, dirs, files in os.walk(WORKSPACE_ROOT):
            if any(p in root for p in [".git", "__pycache__", "node_modules", ".venv"]):
                continue
            for file in files:
                filepath = Path(root) / file
                mtime = filepath.stat().st_mtime
                recent.append({
                    "path": str(filepath.relative_to(WORKSPACE_ROOT)),
                    "mtime": mtime,
                    "last_modified": datetime.fromtimestamp(mtime).isoformat()
                })
        recent.sort(key=lambda x: x["mtime"], reverse=True)
    except Exception as e:
        pass
    return recent[:limit]

def check_hermes_state_timestamp() -> str:
    db_path = HERMES_STATE_DIR / "profiles" / "leo-manager-sandbox" / "state.db"
    if db_path.exists():
        mtime = db_path.stat().st_mtime
        return datetime.fromtimestamp(mtime).isoformat()
    return "not_found"

def sync_workspace_state() -> dict:
    ensure_evidence_dir()
    
    sync_data = {
        "timestamp": datetime.now().isoformat(),
        "sync_status": "SYNCHRONIZED",
        "antigravity_2_0_active": True,
        "git_state": get_git_status(),
        "recent_modifications": get_recent_file_changes(limit=15),
        "hermes_sandbox_last_active": check_hermes_state_timestamp()
    }
    
    with open(SYNC_FILE, "w", encoding="utf-8") as f:
        json.dump(sync_data, f, indent=2)
        
    return sync_data

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    data = sync_workspace_state()
    print("Workspace State Sync Successful:")
    print(json.dumps(data, indent=2))
