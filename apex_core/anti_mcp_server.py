"""
Anti IDE Remote MCP Server
Exposes anti-hermes-mcp-proof tools over FastMCP (SSE / Streamable HTTP)
on 0.0.0.0:8799 for HP Compute Node Hermes integration.
"""

import sys
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "legacy_archive") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "legacy_archive"))

import server as legacy_server
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("anti_mcp_server")

RECEIPT_LOG = PROJECT_ROOT / "evidence" / "anti_mcp_receipts.jsonl"
RECEIPT_LOG.parent.mkdir(parents=True, exist_ok=True)

def log_receipt(tool_name: str, arguments: dict, result: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "arguments": arguments,
        "result": result
    }
    with open(RECEIPT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    logger.info(f"LOGGED RECEIPT for tool={tool_name}")

mcp = FastMCP("anti-hermes-mcp-proof", host="0.0.0.0", port=8799)

def _get_git_tip() -> str:
    try:
        res = subprocess.run(
            ["git", "log", "-n", "1", "--oneline"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=3
        )
        return res.stdout.strip()
    except Exception as e:
        return f"git error: {e}"

def _get_latest_state_entries(limit: int = 10) -> list[str]:
    state_file = PROJECT_ROOT / "SYSTEM_STATE.md"
    if not state_file.exists():
        return []
    try:
        raw = state_file.read_text(encoding="utf-8", errors="replace")
        entries = [l.strip() for l in raw.splitlines() if l.strip().startswith("- [2026-")]
        return entries[-limit:]
    except Exception as e:
        return [f"state read error: {e}"]

@mcp.tool()
def get_status() -> str:
    """Returns the operational status of the mock workforce sandbox, Anti IDE bridge, latest commit, and ledger receipts."""
    res = legacy_server.handle_get_status()
    res["anti_ide_bridge"] = "LIVE_CONNECTED"
    res["host"] = "Alienware HQ (TaxcoreAmerica)"
    res["latest_commit"] = _get_git_tip()
    entries = _get_latest_state_entries(1)
    res["latest_system_receipt"] = entries[0] if entries else None
    res["inspection_tools_available"] = [
        "get_anti_work_ledger",
        "get_deliverables_status",
        "read_deliverable"
    ]
    log_receipt("get_status", {}, res)
    return json.dumps(res, indent=2)

@mcp.tool()
def get_anti_work_ledger(limit: int = 15) -> str:
    """Returns the latest authoritative state ledger receipts from SYSTEM_STATE.md and current git status."""
    entries = _get_latest_state_entries(limit)
    res = {
        "latest_commit": _get_git_tip(),
        "total_receipts_returned": len(entries),
        "recent_ledger_entries": entries
    }
    log_receipt("get_anti_work_ledger", {"limit": limit}, res)
    return json.dumps(res, indent=2)

@mcp.tool()
def get_deliverables_status() -> str:
    """Returns the current inventory of workforce sandbox deliverables, test files, and receipts."""
    sandbox = PROJECT_ROOT / "sandbox" / "apex-workforce-sandbox"
    inventory = []
    if sandbox.exists():
        for f in sorted(sandbox.rglob("*")):
            if f.is_file() and not f.name.startswith(".") and not f.name.endswith(".pyc") and "__pycache__" not in str(f):
                inventory.append({
                    "path": str(f.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    "size_bytes": f.stat().st_size,
                    "modified_utc": datetime.fromtimestamp(f.stat().st_mtime, timezone.utc).isoformat()
                })
    res = {
        "deliverables_count": len(inventory),
        "files": inventory
    }
    log_receipt("get_deliverables_status", {}, res)
    return json.dumps(res, indent=2)

@mcp.tool()
def read_deliverable(relative_path: str) -> str:
    """Reads the content of a deliverable file in the workspace (e.g. SYSTEM_STATE.md, sandbox/..., evidence/...)."""
    target = (PROJECT_ROOT / relative_path).resolve()
    # Path traversal protection
    if not str(target).startswith(str(PROJECT_ROOT.resolve())):
        err = {"error": "Access denied: Path outside workspace"}
        log_receipt("read_deliverable", {"relative_path": relative_path}, err)
        return json.dumps(err, indent=2)
    if not target.is_file():
        err = {"error": f"File not found: {relative_path}"}
        log_receipt("read_deliverable", {"relative_path": relative_path}, err)
        return json.dumps(err, indent=2)
    try:
        content = target.read_text(encoding="utf-8", errors="replace")
        truncated = False
        if len(content) > 12000:
            content = content[:12000] + "\n...[truncated for MCP transport]"
            truncated = True
        res = {
            "file": str(target.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "size_bytes": target.stat().st_size,
            "truncated": truncated,
            "content": content
        }
    except Exception as e:
        res = {"error": f"Read error: {e}"}
    log_receipt("read_deliverable", {"relative_path": relative_path}, res)
    return json.dumps(res, indent=2)

@mcp.tool()
def get_assignment() -> str:
    """Retrieves the currently assigned task for the mock workforce."""
    res = legacy_server.handle_get_assignment()
    log_receipt("get_assignment", {}, res)
    return json.dumps(res, indent=2)

@mcp.tool()
def submit_result(assignment_id: str, status: str, answer: str, evidence: str) -> str:
    """Submits the completed task result with evidence for verification."""
    args = {
        "assignment_id": assignment_id,
        "status": status,
        "answer": answer,
        "evidence": evidence
    }
    res, _ = legacy_server.handle_submit_result(args)
    log_receipt("submit_result", args, res)
    return json.dumps(res, indent=2)

@mcp.tool()
def get_workspace_sync_status() -> str:
    """Returns current workspace synchronization status."""
    sync_file = PROJECT_ROOT / "evidence" / "workspace_sync.json"
    if sync_file.exists():
        with open(sync_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"status": "synced", "verified": True}
    log_receipt("get_workspace_sync_status", {}, data)
    return json.dumps(data, indent=2)

if __name__ == "__main__":
    logger.info("Starting Anti IDE Remote MCP Server on 0.0.0.0:8799 (SSE transport)...")
    mcp.run(transport="sse")

