#!/usr/bin/env python3
"""
Test client to validate anti-hermes-mcp-proof server over stdio JSON-RPC.
Executes initialization, tool listing, positive proof workflow, and negative rejection test.
"""

import subprocess
import json
import sys
from pathlib import Path

def run_test():
    server_script = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\legacy_archive\server.py").resolve()
    evidence_file = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\evidence\submitted-result.json").resolve()
    
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
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    init_res = send_recv(init_req)
    results["initialize"] = init_res

    # 2. List tools
    tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    tools_res = send_recv(tools_req)
    results["tools_list"] = tools_res
    tool_names = [t["name"] for t in tools_res.get("result", {}).get("tools", [])]
    results["discovered_tool_names"] = tool_names
    results["tool_count"] = len(tool_names)

    # 3. Call get_status
    status_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "get_status", "arguments": {}}
    }
    status_res = send_recv(status_req)
    results["get_status"] = status_res

    # 4. Call get_assignment
    assignment_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {"name": "get_assignment", "arguments": {}}
    }
    assignment_res = send_recv(assignment_req)
    results["get_assignment"] = assignment_res
    
    assignment_content = json.loads(assignment_res["result"]["content"][0]["text"])
    assignment_id = assignment_content.get("assignment_id")

    # 5. Execute task: Calculate 12 + 19 = 31
    answer = 12 + 19
    evidence = "Arithmetic verification: 12 + 19 = 31 performed under sandbox isolation."

    # 6. Call submit_result
    submit_req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "submit_result",
            "arguments": {
                "assignment_id": assignment_id,
                "status": "completed",
                "answer": answer,
                "evidence": evidence
            }
        }
    }
    submit_res = send_recv(submit_req)
    results["submit_result_positive"] = submit_res

    # Read accepted file and record timestamp / content
    if evidence_file.exists():
        with open(evidence_file, "r", encoding="utf-8") as f:
            accepted_file_content = json.load(f)
        results["accepted_file_content"] = accepted_file_content
        results["file_exists"] = True
    else:
        results["file_exists"] = False
        results["accepted_file_content"] = None

    # 7. Negative test: Call submit_result with wrong ID
    neg_req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "submit_result",
            "arguments": {
                "assignment_id": "MCP-PROOF-INVALID-999",
                "status": "completed",
                "answer": 999,
                "evidence": "Tampered submission attempt"
            }
        }
    }
    neg_res = send_recv(neg_req)
    results["submit_result_negative"] = neg_res

    # Verify accepted file was NOT overwritten with invalid content
    if evidence_file.exists():
        with open(evidence_file, "r", encoding="utf-8") as f:
            after_neg_content = json.load(f)
        results["negative_test_file_unmodified"] = (after_neg_content == accepted_file_content)
    else:
        results["negative_test_file_unmodified"] = False

    proc.stdin.close()
    proc.terminate()

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_test()
