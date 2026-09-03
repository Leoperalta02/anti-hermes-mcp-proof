#!/usr/bin/env python3
"""
hermes_sandbox_server.py: Read-Only Hermes Sandbox Adapter MCP Server
Exposes 4 bounded tools for inspecting Hermes sandbox state and staging results.
"""

import sys
import json
import os
import sqlite3
from pathlib import Path

PROFILE_DIR = Path(r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\leo-manager-sandbox").resolve()
STATE_DB = PROFILE_DIR / "state.db"
CONFIG_FILE = PROFILE_DIR / "config.yaml"
PROFILE_FILE = PROFILE_DIR / "profile.yaml"

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()
EVIDENCE_DIR = WORKSPACE_ROOT / "evidence"
STAGED_RESULT_FILE = EVIDENCE_DIR / "staged-hermes-result.json"

TOOLS_SCHEMA = [
    {
        "name": "get_hermes_sandbox_status",
        "description": "Returns profile name, local model route, cloud-disabled status, and whether the sandbox is reachable (read-only).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "list_hermes_sandbox_assignments",
        "description": "Lists safe assignment IDs, states, timestamps, and concise task summaries for the sandbox profile (read-only).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of assignments to return (default 20)."
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "read_hermes_sandbox_assignment",
        "description": "Reads goal, state, child/parent IDs, completion metadata, and result availability for an assignment in leo-manager-sandbox (read-only).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "assignment_id": {
                    "type": "string",
                    "description": "The unique delegation/assignment ID (e.g. deleg_8ef5cc69)."
                }
            },
            "required": ["assignment_id"],
            "additionalProperties": False
        }
    },
    {
        "name": "stage_hermes_result",
        "description": "Stages a proposed result locally in proof evidence without writing to Hermes state, HQ, or authoritative records.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "assignment_id": {
                    "type": "string",
                    "description": "The unique assignment ID in leo-manager-sandbox."
                },
                "proposed_result": {
                    "type": ["string", "object"],
                    "description": "The proposed result or calculation output to stage."
                },
                "reasoning": {
                    "type": "string",
                    "description": "Concise reasoning or staging rationale."
                }
            },
            "required": ["assignment_id", "proposed_result"],
            "additionalProperties": False
        }
    }
]

def handle_get_sandbox_status():
    reachable = PROFILE_DIR.exists() and STATE_DB.exists()
    
    model_default = "unknown"
    provider = "unknown"
    base_url = "unknown"
    free_only = True
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                current_section = None
                for raw_line in f:
                    line = raw_line.rstrip()
                    if not line or line.startswith("#"):
                        continue
                    if not raw_line.startswith(" ") and not raw_line.startswith("\t") and ":" in line:
                        current_section = line.split(":", 1)[0].strip()
                        continue
                    
                    stripped = line.strip()
                    if current_section == "model":
                        if stripped.startswith("default:"):
                            model_default = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                        elif stripped.startswith("provider:"):
                            provider = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                        elif stripped.startswith("base_url:"):
                            base_url = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                    elif current_section == "auxiliary":
                        if stripped.startswith("free_only:"):
                            free_only = (stripped.split(":", 1)[1].strip().lower() == "true")
        except Exception:
            pass

    db_ok = False
    if reachable:
        try:
            conn = sqlite3.connect(f"file:{STATE_DB.as_posix()}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM async_delegations")
            cur.fetchone()
            conn.close()
            db_ok = True
        except Exception:
            db_ok = False

    return {
        "profile_name": "leo-manager-sandbox",
        "sandbox_reachable": reachable,
        "database_connected": db_ok,
        "local_model_route": f"{model_default} via {provider} ({base_url})",
        "cloud_disabled": {
            "free_only": free_only,
            "provider": provider,
            "external_api_active": False
        },
        "authority": "sandbox-read-only"
    }

def handle_list_assignments(args):
    limit = args.get("limit", 20)
    if not isinstance(limit, int) or limit <= 0:
        limit = 20
    if limit > 100:
        limit = 100

    if not STATE_DB.exists():
        return {"error": "state.db not found", "assignments": []}, True

    try:
        conn = sqlite3.connect(f"file:{STATE_DB.as_posix()}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT delegation_id, state, dispatched_at, completed_at, delivery_state, task_json, result_json "
            "FROM async_delegations ORDER BY dispatched_at DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        conn.close()

        assignments = []
        for r in rows:
            task_data = {}
            if r["task_json"]:
                try:
                    task_data = json.loads(r["task_json"])
                except Exception:
                    pass

            goal = task_data.get("goal") or (task_data.get("goals")[0] if task_data.get("goals") else "")
            summary_snippet = goal[:120] + "..." if len(goal) > 120 else goal

            is_terminal = (r["state"] == "completed" and r["completed_at"] is not None)

            assignments.append({
                "assignment_id": r["delegation_id"],
                "state": r["state"],
                "terminal_completion": is_terminal,
                "dispatched_at": r["dispatched_at"],
                "completed_at": r["completed_at"],
                "delivery_state": r["delivery_state"],
                "task_summary": summary_snippet,
                "has_result": bool(r["result_json"])
            })

        return {"profile": "leo-manager-sandbox", "count": len(assignments), "assignments": assignments}, False
    except Exception as e:
        return {"error": f"Failed to list assignments: {str(e)}"}, True

def handle_read_assignment(args):
    assignment_id = args.get("assignment_id")
    if not assignment_id or not isinstance(assignment_id, str):
        return {"error": "Invalid or missing assignment_id"}, True

    if not STATE_DB.exists():
        return {"error": "state.db not found"}, True

    try:
        conn = sqlite3.connect(f"file:{STATE_DB.as_posix()}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT delegation_id, origin_session, origin_ui_session_id, parent_session_id, "
            "state, dispatched_at, completed_at, updated_at, task_json, result_json, delivery_state "
            "FROM async_delegations WHERE delegation_id = ?",
            (assignment_id,)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return {
                "error": f"Assignment ID '{assignment_id}' was not found in profile 'leo-manager-sandbox'."
            }, True

        task_data = {}
        if row["task_json"]:
            try:
                task_data = json.loads(row["task_json"])
            except Exception:
                pass

        result_data = {}
        result_summary = None
        if row["result_json"]:
            try:
                result_data = json.loads(row["result_json"])
                if "results" in result_data and isinstance(result_data["results"], list) and len(result_data["results"]) > 0:
                    result_summary = result_data["results"][0].get("summary")
                elif "summary" in result_data:
                    result_summary = result_data.get("summary")
                elif "error" in result_data:
                    result_summary = f"Error: {result_data.get('error')}"
            except Exception:
                result_summary = "Raw result unparsable"

        is_terminal = (row["state"] == "completed" and row["completed_at"] is not None)

        return {
            "assignment_id": row["delegation_id"],
            "profile": "leo-manager-sandbox",
            "goal": task_data.get("goal") or (task_data.get("goals")[0] if task_data.get("goals") else ""),
            "role": task_data.get("role", "unknown"),
            "state": row["state"],
            "terminal_completed": is_terminal,
            "dispatched_at": row["dispatched_at"],
            "completed_at": row["completed_at"],
            "parent_session_id": row["parent_session_id"],
            "origin_session": row["origin_session"],
            "delivery_state": row["delivery_state"],
            "result_available": bool(row["result_json"]),
            "result_summary": result_summary
        }, False
    except Exception as e:
        return {"error": f"Failed to read assignment: {str(e)}"}, True

def handle_stage_result(args):
    assignment_id = args.get("assignment_id")
    proposed_result = args.get("proposed_result")
    reasoning = args.get("reasoning", "")

    if not assignment_id or not isinstance(assignment_id, str):
        return {"error": "Invalid or missing assignment_id", "success": False}, True
    if proposed_result is None:
        return {"error": "Missing proposed_result", "success": False}, True

    # Validate assignment exists in leo-manager-sandbox read-only
    if not STATE_DB.exists():
        return {"error": "state.db not found in leo-manager-sandbox", "success": False}, True

    try:
        conn = sqlite3.connect(f"file:{STATE_DB.as_posix()}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT state FROM async_delegations WHERE delegation_id = ?", (assignment_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return {
                "error": f"Validation failed: Assignment '{assignment_id}' does not belong to 'leo-manager-sandbox'.",
                "success": False
            }, True
    except Exception as e:
        return {"error": f"Database validation error: {str(e)}", "success": False}, True

    # Staging write ONLY to proof workspace evidence directory
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    staged_payload = {
        "assignment_id": assignment_id,
        "profile": "leo-manager-sandbox",
        "status": "staged",
        "authoritative": False,
        "proposed_result": proposed_result,
        "reasoning": reasoning,
        "destination_file": str(STAGED_RESULT_FILE),
        "note": "Staged only. Not written to Hermes state or authoritative records."
    }

    try:
        with open(STAGED_RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(staged_payload, f, indent=2)
        return {
            "success": True,
            "status": "staged",
            "message": "Result successfully staged in isolated proof evidence. Not committed to Hermes.",
            "file": str(STAGED_RESULT_FILE)
        }, False
    except Exception as e:
        return {"error": f"Failed to write staged result file: {str(e)}", "success": False}, True

def process_request(request):
    method = request.get("method")
    msg_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "hermes-sandbox-adapter",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {}
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_SCHEMA
            }
        }
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name == "get_hermes_sandbox_status":
            res = handle_get_sandbox_status()
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": False
                }
            }
        elif tool_name == "list_hermes_sandbox_assignments":
            res, is_err = handle_list_assignments(tool_args)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": is_err
                }
            }
        elif tool_name == "read_hermes_sandbox_assignment":
            res, is_err = handle_read_assignment(tool_args)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": is_err
                }
            }
        elif tool_name == "stage_hermes_result":
            res, is_err = handle_stage_result(tool_args)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": is_err
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    else:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
        return None

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = process_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
