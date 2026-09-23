$python = "C:\Program Files\Python312\python.exe"
$script = "C:\LEO-LAB-ANTIGRAVITY\hermes-state\scripts\apex_edge_tunnel.py"
while ($true) {
    & $python $script
    Start-Sleep -Seconds 5
}
