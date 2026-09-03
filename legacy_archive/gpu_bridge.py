import paramiko
import threading
import select
import socket
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

# Reverse port forwarding from remote VPS (127.0.0.1:11434) to local Windows PC (127.0.0.1:11434)
VPS_HOST = '159.223.183.138'
VPS_PORT = 22
VPS_USER = 'root'
VPS_PASS = '25021121Wow'

REMOTE_PORT = 11434
LOCAL_HOST = '127.0.0.1'
LOCAL_PORT = 11434

def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward('', server_port)
    print(f"[*] Reverse tunnel listening on VPS port {server_port} -> forwarding to local {remote_host}:{remote_port}")
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, remote_host, remote_port))
        thr.daemon = True
        thr.start()

def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"[!] Forwarding request to {host}:{port} failed: {e}")
        chan.close()
        return

    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()

def main():
    print(f"Connecting to VPS {VPS_HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASS, timeout=10)
    
    transport = client.get_transport()
    print("[+] SSH connection established.")
    
    # Start the reverse forwarding loop
    thr = threading.Thread(target=reverse_forward_tunnel, args=(REMOTE_PORT, LOCAL_HOST, LOCAL_PORT, transport))
    thr.daemon = True
    thr.start()
    
    # Keep main alive
    try:
        while True:
            time.sleep(1)
            if not transport.is_active():
                print("[!] Transport died, reconnecting...")
                break
    except KeyboardInterrupt:
        print("\nStopping tunnel...")
    finally:
        client.close()

if __name__ == '__main__':
    main()
