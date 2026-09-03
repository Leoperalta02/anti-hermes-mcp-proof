#!/usr/bin/env python3
"""
vps_deploy.py: Deploys updated web files, handlers, and Watchdog engine to VPS (159.223.183.138).
Restarts systemd service to apply all Training Dojo fixes live.
"""

import paramiko
import os
import sys
from pathlib import Path

VPS_HOST = '159.223.183.138'
VPS_PORT = 22
VPS_USER = 'root'
VPS_PASS = '25021121Wow'

WORKSPACE_ROOT = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof").resolve()

def deploy_to_vps():
    print(f"Connecting to VPS {VPS_HOST} via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASS, timeout=10)
    print("SSH Connected successfully.")

    # Find service path on remote VPS
    stdin, stdout, stderr = ssh.exec_command("systemctl status leo-os-office || systemctl list-units | grep -i office || pwd")
    out = stdout.read().decode('utf-8', errors='replace')
    print("Remote Service Status / Path Info:\n", out)

    # Find where index.html / server.py are located on remote VPS
    stdin, stdout, stderr = ssh.exec_command("find / -name 'index.html' 2>/dev/null | grep -i 'real-estate\\|office\\|hermes\\|anti'")
    remote_paths = stdout.read().decode('utf-8', errors='replace').strip().splitlines()
    print("Remote web files found:", remote_paths)

    sftp = ssh.open_sftp()
    
    # Upload local files to remote web directory
    local_index = WORKSPACE_ROOT / "real-estate-web" / "index.html"
    local_server = WORKSPACE_ROOT / "real-estate-web" / "server.py"
    local_playbook = WORKSPACE_ROOT / "NIKKI_CONVERSION_PLAYBOOK.md"
    local_watchdog = WORKSPACE_ROOT / "hq_watchdog.py"

    for rpath in remote_paths:
        rdir = os.path.dirname(rpath)
        print(f"Deploying to remote folder: {rdir}")
        try:
            sftp.put(str(local_index), f"{rdir}/index.html")
            print(f"Uploaded index.html -> {rdir}/index.html")
            sftp.put(str(local_server), f"{rdir}/server.py")
            print(f"Uploaded server.py -> {rdir}/server.py")
            sftp.put(str(local_playbook), f"{os.path.dirname(rdir)}/NIKKI_CONVERSION_PLAYBOOK.md")
            print(f"Uploaded NIKKI_CONVERSION_PLAYBOOK.md -> {os.path.dirname(rdir)}/NIKKI_CONVERSION_PLAYBOOK.md")
            sftp.put(str(local_watchdog), f"{os.path.dirname(rdir)}/hq_watchdog.py")
            print(f"Uploaded hq_watchdog.py -> {os.path.dirname(rdir)}/hq_watchdog.py")
        except Exception as e:
            print(f"SFTP upload error for {rdir}: {e}")

    # Restart web service
    stdin, stdout, stderr = ssh.exec_command("systemctl restart leo-os-office || systemctl restart office || pkill -f 'python.*server.py'")
    res = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print("Service restart result:", res, err)

    sftp.close()
    ssh.close()
    print("=== VPS DEPLOYMENT COMPLETED ===")

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    deploy_to_vps()
