"""
Cursor Coding Agent Fallback Harness & Dispatcher
=================================================
Allows Leo, Hermes, or Anti to invoke Cursor Coding Agent with full autonomous
system tools (file read/write, bash/terminal, and native MCP tools).

Usage:
    python apex_core/cursor_agent_bridge.py "Audit and fix any failing tests"
    python apex_core/cursor_agent_bridge.py --yolo "Deploy changes"
"""

import subprocess
import sys
import os
import argparse

DEFAULT_MODEL = "cursor-grok-4.5-medium"

def run_cursor_agent(prompt: str, model: str = None, yolo: bool = True, print_output: bool = True):
    """
    Executes cursor-agent with full computer tool authority.
    Flags:
      -f / --yolo: Force allow shell & file modifications without interactive prompts
      --trust: Trust the workspace
      --approve-mcps: Automatically connect & approve all workspace MCP servers
      -p: Print output to stdout
    """
    cursor_agent_ps1 = os.path.expandvars(r"%LOCALAPPDATA%\cursor-agent\cursor-agent.ps1")
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        cursor_agent_ps1,
        "--trust",
        "--approve-mcps",
    ]
    if yolo:
        cmd.append("-f")
    
    if model:
        cmd.extend(["--model", model])
        
    brevity_prefix = (
        "[STRICT TOKEN HYGIENE: Be concise. DO NOT repeat this prompt, recite rules, or write essay summaries. "
        "State what you are doing in 1 sentence, execute with tools directly, and report result in 1 sentence.]\n\n"
    )
    full_prompt = brevity_prefix + prompt
    cmd.extend(["-p", full_prompt])
    
    print(f">> [CURSOR AGENT HARNESS] Invoking Cursor Coding Agent...")
    print(f">> [PROMPT]: {prompt}\n" + "-" * 60)
    
    result = subprocess.run(cmd, cwd=os.path.abspath("."), capture_output=False, text=True)
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cursor Coding Agent Fallback Harness")
    parser.add_argument("prompt", nargs="+", help="Instruction or task for Cursor Coding Agent")
    parser.add_argument("--model", default=None, help="Target model override")
    parser.add_argument("--no-yolo", action="store_true", help="Require prompt before running dangerous tools")
    args = parser.parse_args()
    
    prompt_str = " ".join(args.prompt)
    exit_code = run_cursor_agent(prompt_str, model=args.model, yolo=not args.no_yolo)
    sys.exit(exit_code)
