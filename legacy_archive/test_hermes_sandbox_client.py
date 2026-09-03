#!/usr/bin/env python3
"""
test_hermes_sandbox_client.py: Validates hermes_sandbox_server.py over stdio JSON-RPC.
Runs read-only inspection tests and negative validation tests.
Does not call stage_hermes_result unless approved.
"""

import subprocess
import json
import sys
from pathlib import Path

def run_test():
    server_script = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\hermes_sandbox_server.py").resolve()
    
    proc = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8"
    )

    def send_recv(msg):
        line = json.dumps(msg) + "\n"
        proc.stdin.write(line)
        proc.stdin.flush()
        out_line = proc.stdout.readline().strip()
        return json.loads(out_line)

    results = {}

    # 1. Initialize
    init_res = send_recv({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-sandbox-client", "version": "1.0.0"}
        }
    })
    results["initialize"] = init_res

    # 2. List tools
    tools_res = send_recv({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    results["tools_list"] = tools_res
    tool_names = [t["name"] for t in tools_res.get("result", {}).get("tools", [])]
    results["tools_count"] = len(tool_names)
    results["tools"] = tool_names

    # 3. Call get_hermes_sandbox_status
    status_res = send_recv({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "get_hermes_sandbox_status", "arguments": {}}
    })
    results["get_hermes_sandbox_status"] = json.loads(status_res["result"]["content"][0]["text"])

    # 4. Call list_hermes_sandbox_assignments
    list_res = send_recv({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "list_hermes_sandbox_assignments", "arguments": {"limit": 5}}
    })
    results["list_hermes_sandbox_assignments"] = json.loads(list_res["result"]["content"][0]["text"])

    # 5. Call read_hermes_sandbox_assignment with valid ID
    valid_id = "deleg_8ef5cc69"
    read_res = send_recv({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {"name": "read_hermes_sandbox_assignment", "arguments": {"assignment_id": valid_id}}
    })
    results["read_hermes_sandbox_assignment_valid"] = json.loads(read_res["result"]["content"][0]["text"])

    # 6. Call read_hermes_sandbox_assignment with invalid ID (Negative boundary test)
    neg_read_res = send_recv({
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {"name": "read_hermes_sandbox_assignment", "arguments": {"assignment_id": "non_existent_or_foreign_profile_id"}}
    })
    results["read_hermes_sandbox_assignment_invalid"] = {
        "isError": neg_read_res["result"].get("isError", False),
        "content": json.loads(neg_read_res["result"]["content"][0]["text"])
    }

    proc.stdin.close()
    proc.terminate()

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_test()
