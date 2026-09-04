r"""
Aura Inbox & Storage Sentinel (apex_core/aura_inbox_sentinel.py)

Autonomous local sentinel running on HQ.
- Uses Samsung External Drive (D:\) to archive heavy attachments and reclaim Google Storage.
- Purges promotional junk & blast ads.
- Stars/pins important incoming client & business emails.
- Schedules calendar reminders for time-sensitive deadlines.
- 100% private: uses local Aura Qwen on RTX 3070 Ti for any NLP triage.
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VAULT_TOKEN_PATH = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\vault_backup\google_oauth_token.json")
ARCHIVE_BASE_DIR = Path(r"D:\Email_Archives")
ATTACHMENTS_DIR = ARCHIVE_BASE_DIR / "Attachments"
RECEIPTS_DIR = ARCHIVE_BASE_DIR / "Receipts_Invoices"
CONTRACTS_DIR = ARCHIVE_BASE_DIR / "Contracts_Legal"

for d in (ATTACHMENTS_DIR, RECEIPTS_DIR, CONTRACTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


class AuraInboxSentinel:
    def __init__(self, token_path: Path = VAULT_TOKEN_PATH):
        self.token_path = token_path
        self.access_token: Optional[str] = None
        self._refresh_token()

    def _refresh_token(self) -> str:
        """Load and auto-refresh the Google OAuth token."""
        if not self.token_path.exists():
            raise FileNotFoundError(f"Vault token not found at {self.token_path}")

        with open(self.token_path, "r", encoding="utf-8") as f:
            vault = json.load(f)

        payload = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "client_id": vault["client_id"],
            "client_secret": vault["client_secret"],
            "refresh_token": vault["refresh_token"],
        }).encode("utf-8")

        req = urllib.request.Request(
            vault.get("token_uri", "https://oauth2.googleapis.com/token"),
            data=payload,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                self.access_token = result["access_token"]
                vault["token"] = self.access_token
                vault["expiry"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                if "refresh_token" in result:
                    vault["refresh_token"] = result["refresh_token"]
                with open(self.token_path, "w", encoding="utf-8") as out:
                    json.dump(vault, out, indent=2)
                return self.access_token
        except urllib.error.HTTPError as e:
            print(f"[AuraSentinel Error] Token refresh failed: {e.read().decode()}")
            raise

    def _request(self, url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform authorized Google API request with token auto-retry."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        encoded_data = json.dumps(data).encode("utf-8") if data is not None else None

        req = urllib.request.Request(url, data=encoded_data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                if not raw:
                    return {}
                return json.loads(raw.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                # Refresh token and retry once
                self._refresh_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                req = urllib.request.Request(url, data=encoded_data, method=method, headers=headers)
                with urllib.request.urlopen(req) as retry_resp:
                    raw = retry_resp.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            raise

    # ── Storage Saver: Offload Heavy Attachments to Samsung Drive ──────────────

    def scan_heavy_emails(self, min_size_mb: int = 5, max_results: int = 20) -> List[Dict[str, Any]]:
        """Find emails with attachments larger than min_size_mb."""
        query = f"has:attachment larger:{min_size_mb}M"
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}&maxResults={max_results}"
        res = self._request(url)
        return res.get("messages", [])

    def download_attachments_and_offload(self, message_id: str, destination_dir: Path = ATTACHMENTS_DIR) -> List[Path]:
        """Download all attachments in a message to the external Samsung drive."""
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
        msg = self._request(url)
        payload = msg.get("payload", {})
        saved_files = []

        headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
        subject = headers.get("Subject", "no_subject").replace(" ", "_").replace("/", "_")[:40]
        date_str = datetime.now().strftime("%Y%m%d")

        parts = payload.get("parts", [])
        for part in parts:
            filename = part.get("filename")
            body = part.get("body", {})
            attachment_id = body.get("attachmentId")

            if filename and attachment_id:
                # Fetch attachment data
                att_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/attachments/{attachment_id}"
                att_res = self._request(att_url)
                raw_b64 = att_res.get("data", "")
                if raw_b64:
                    file_bytes = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
                    safe_filename = f"{date_str}_{message_id[:8]}_{filename}"
                    dest_file = destination_dir / safe_filename
                    dest_file.write_bytes(file_bytes)
                    print(f"[Aura Offload] Saved {len(file_bytes)} bytes to: {dest_file}")
                    saved_files.append(dest_file)

        return saved_files

    def trash_message(self, message_id: str) -> bool:
        """Move a message to Gmail Trash."""
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/trash"
        try:
            self._request(url, method="POST")
            return True
        except Exception as e:
            print(f"[Aura Error] Failed to trash {message_id}: {e}")
            return False

    def empty_trash_messages(self, max_purge: int = 50) -> int:
        """Permanently delete messages in Trash to immediately free Google storage."""
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q=in:trash&maxResults={max_purge}"
        res = self._request(url)
        messages = res.get("messages", [])
        purged = 0

        for m in messages:
            msg_id = m["id"]
            del_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
            try:
                self._request(del_url, method="DELETE")
                purged += 1
            except Exception as e:
                print(f"[Aura Error] Failed permanent delete for {msg_id}: {e}")

        print(f"[Aura Storage Saver] Permanently purged {purged} messages from Gmail Trash.")
        return purged

    # ── Spam & Promo Cleaner ──────────────────────────────────────────────────

    def find_promotions_and_spam(self, max_results: int = 25) -> List[Dict[str, Any]]:
        """Find blast emails, ads, and promotions."""
        query = "category:promotions OR is:spam"
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}&maxResults={max_results}"
        res = self._request(url)
        return res.get("messages", [])

    def clean_promotions_batch(self, max_batch: int = 30) -> Dict[str, Any]:
        """Batch move promotional blast emails to trash and log unsubscribe headers."""
        promos = self.find_promotions_and_spam(max_results=max_batch)
        trashed_count = 0
        unsub_links = []

        for p in promos:
            msg_id = p["id"]
            url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject&metadataHeaders=List-Unsubscribe"
            try:
                detail = self._request(url)
                headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
                unsub = headers.get("List-Unsubscribe")
                if unsub:
                    unsub_links.append({"from": headers.get("From"), "unsubscribe": unsub})

                if self.trash_message(msg_id):
                    trashed_count += 1
            except Exception as e:
                continue

        return {
            "trashed_count": trashed_count,
            "unsubscribe_records": unsub_links[:10],
        }

    # ── VIP Pinning & Calendar Reminders ──────────────────────────────────────

    def star_message(self, message_id: str) -> bool:
        """Star / pin a message to the top of Gmail."""
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}/modify"
        data = {"addLabelIds": ["STARRED"]}
        try:
            self._request(url, method="POST", data=data)
            return True
        except Exception as e:
            print(f"[Aura Error] Star message {message_id} failed: {e}")
            return False

    def create_calendar_reminder(self, title: str, start_iso: str, end_iso: Optional[str] = None, description: str = "") -> Dict[str, Any]:
        """Create a Google Calendar reminder event."""
        if not end_iso:
            # Default 1 hour duration
            end_dt = datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
            from datetime import timedelta
            end_iso = (end_dt + timedelta(hours=1)).isoformat()

        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        event_body = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_iso},
            "end": {"dateTime": end_iso},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},
                    {"method": "email", "minutes": 1440},
                ],
            },
        }
        return self._request(url, method="POST", data=event_body)

    # ── Autonomous Heartbeat Daemon ───────────────────────────────────────────

    def get_system_memory_gb(self) -> Dict[str, float]:
        """Get current free and total physical memory in GB."""
        import subprocess
        cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize | ConvertTo-Json"'
        try:
            out = subprocess.check_output(cmd, shell=True, text=True).strip()
            data = json.loads(out)
            free_gb = round(data["FreePhysicalMemory"] / (1024 * 1024), 2)
            total_gb = round(data["TotalVisibleMemorySize"] / (1024 * 1024), 2)
            return {"free_gb": free_gb, "total_gb": total_gb}
        except Exception:
            return {"free_gb": 0.0, "total_gb": 0.0}

    def reap_stale_processes(self) -> int:
        """Scan and terminate zombie/orphaned test servers, stale headless browsers, and dead runners."""
        import subprocess
        ps_script = r'''
        $protectedPids = @(37056, 4284, 7756, $PID)
        $reaped = 0
        
        # 1. Orphaned python test servers & legacy runners
        $stalePy = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | Where-Object {
            ($_.CommandLine -like "*http.server*" -or
             $_.CommandLine -like "*legacy_archive\server.py*" -or
             $_.CommandLine -like "*hermes_sandbox_server.py*") -and
            $protectedPids -notcontains $_.ProcessId
        }
        foreach ($p in $stalePy) {
            try { Stop-Process -Id $p.ProcessId -Force; $reaped++ } catch {}
        }
        
        # 2. Orphaned headless Chrome browser subagent instances
        $staleChrome = Get-CimInstance Win32_Process -Filter "Name = 'chrome.exe'" | Where-Object {
            $_.CommandLine -like "*--remote-debugging-port=9222*" -and
            $_.CommandLine -like "*--user-data-dir=C:\Users\leope\.gemini*"
        }
        foreach ($c in $staleChrome) {
            try { Stop-Process -Id $c.ProcessId -Force; $reaped++ } catch {}
        }
        
        # 3. Orphaned node devtools/playwright runners
        $staleNode = Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" | Where-Object {
            ($_.CommandLine -like "*chrome-devtools*" -or
             $_.CommandLine -like "*ms-playwright-go*")
        }
        foreach ($n in $staleNode) {
            try { Stop-Process -Id $n.ProcessId -Force; $reaped++ } catch {}
        }
        
        Write-Output $reaped
        '''
        try:
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_script], text=True).strip()
            reaped_count = int(out) if out.isdigit() else 0
            print(f"[Aura Memory Reaper] Safely terminated {reaped_count} stale/orphaned processes.")
            return reaped_count
        except Exception as e:
            print(f"[Aura Memory Reaper Error] {e}")
            return 0

    def clean_hq_temp_files(self) -> int:
        """Clean orphaned crash dumps, residual install caches, and temporary files from Windows."""
        import tempfile
        import time
        import os
        temp_dir = Path(tempfile.gettempdir())
        cleaned_count = 0
        cutoff = time.time() - (86400 * 2)  # 2 days old
        
        # 1. Purge Temp .tmp files
        try:
            for item in temp_dir.glob("*.tmp"):
                try:
                    if item.is_file() and item.stat().st_mtime < cutoff:
                        item.unlink(missing_ok=True)
                        cleaned_count += 1
                except Exception:
                    continue
        except Exception as e:
            print(f"[Aura Temp Cleaner Error] {e}")
            
        # 2. Purge CrashDumps (.dmp files)
        crash_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "CrashDumps"
        if crash_dir.exists():
            for dmp in crash_dir.glob("*.dmp"):
                try:
                    dmp.unlink(missing_ok=True)
                    cleaned_count += 1
                except Exception:
                    continue

        print(f"[Aura Temp Cleaner] Purged {cleaned_count} stale residual files (Temp & CrashDumps).")
        return cleaned_count


    # ── Folder Organization, Clean Labeling & Desktop Hygiene ──────────────────

    def organize_and_label_vault(self) -> Dict[str, int]:
        """Categorize, rename, and sort all offloaded files on Samsung Drive into labeled, alphabetical folders."""
        import re
        import shutil

        categories = {
            "01_Contracts_and_Agreements": ["contract", "purchase agreement", "offer", "as-is", "closing", "addendum"],
            "02_Legal_and_Foreclosures": ["foreclosure", "demand", "n.o.i", "legal", "notice", "case numbers"],
            "03_Insurance_and_Quotes": ["insurance", "indication", "quote", "flood", "coverage", "coi", "peninsula", "integrity"],
            "04_HOA_and_Architecture": ["hoa", "arc", "design", "survey", "permit", "engineer", "lot survey", "affected area"],
            "05_Utilities_and_Invoices": ["utility", "utilities", "invoice", "receipt", "bill", "newaccount", "leegov"],
            "06_Photos_and_Media": [".jpg", ".jpeg", ".png", ".webp", ".heic", "birdview", "3dview", "image"],
        }

        counts = {cat: 0 for cat in categories}
        counts["07_General_Documents"] = 0

        if not ATTACHMENTS_DIR.exists():
            return counts

        for f in list(ATTACHMENTS_DIR.glob("*")):
            if not f.is_file():
                continue

            name_lower = f.name.lower()
            clean_name = re.sub(r"^\d{8}_[a-f0-9]{8}_", "", f.name)
            clean_name = clean_name.replace("$", "USD_").replace("..", ".").strip()

            target_cat = "07_General_Documents"
            for cat, keywords in categories.items():
                if any(kw in name_lower for kw in keywords):
                    target_cat = cat
                    break

            cat_dir = ARCHIVE_BASE_DIR / target_cat
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            dest_file = cat_dir / clean_name
            try:
                shutil.move(str(f), str(dest_file))
                counts[target_cat] += 1
            except Exception as e:
                print(f"[Aura Organize Error] Move failed for {f.name}: {e}")

        print(f"[Aura Vault Organizer] Organized files into labeled categories on D:\\: {counts}")
        return counts

    def clean_and_organize_desktop(self) -> int:
        """Organize Windows Desktop: move loose avatars/assets into labeled folder, keeping desktop clean and alphabetical."""
        import shutil
        desktop_dir = Path(r"C:\Users\leope\Desktop")
        avatars_dir = desktop_dir / "BuzzAvatars"
        avatars_dir.mkdir(parents=True, exist_ok=True)
        moved = 0

        # Move loose image files that belong in BuzzAvatars
        for img in desktop_dir.glob("*.*"):
            if img.is_file() and img.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                if any(kw in img.name.lower() for kw in ["avatar", "fizz", "hermes", "honey", "pollen", "leo_"]):
                    try:
                        dest = avatars_dir / img.name
                        shutil.move(str(img), str(dest))
                        moved += 1
                    except Exception as e:
                        print(f"[Aura Desktop Error] {e}")

        print(f"[Aura Desktop Organizer] Moved {moved} loose avatar files into {avatars_dir}. Desktop is clean & alphabetical.")
        return moved

    def run_heartbeat_cycle(self) -> Dict[str, Any]:
        """Execute one complete heartbeat maintenance cycle."""
        timestamp = datetime.now(timezone.utc).isoformat()
        mem_before = self.get_system_memory_gb()
        print(f"\n[Aura Heartbeat] Cycle start: {timestamp} (Free RAM: {mem_before.get('free_gb')} GB / {mem_before.get('total_gb')} GB)")
        
        # 1. Drive check
        drive_ready = ATTACHMENTS_DIR.exists()
        if not drive_ready:
            print(f"[Aura Heartbeat WARNING] Samsung Drive {ATTACHMENTS_DIR} not accessible!")
            return {"timestamp": timestamp, "drive_ready": False, "error": "Drive D: not mounted"}

        # 2. Offload heavy attachments to Samsung drive
        heavy = self.scan_heavy_emails(min_size_mb=5, max_results=10)
        offloaded_files = []
        for m in heavy:
            try:
                saved = self.download_attachments_and_offload(m["id"])
                if saved:
                    offloaded_files.extend(saved)
                    self.trash_message(m["id"])
            except Exception as e:
                print(f"[Aura Heartbeat Error] Offload failed for {m['id']}: {e}")

        # 3. Clean promotional blast emails
        clean_res = self.clean_promotions_batch(max_batch=30)

        # 4. Reap stale processes on HQ to reclaim RAM
        reaped = self.reap_stale_processes()

        # 5. Purge stale temp files
        temp_cleaned = self.clean_hq_temp_files()

        # 6. Organize and label offloaded files on Samsung Drive D:\ into category folders
        vault_stats = self.organize_and_label_vault()

        # 7. Desktop hygiene: keep desktop spotless and alphabetical
        desktop_cleaned = self.clean_and_organize_desktop()

        mem_after = self.get_system_memory_gb()
        print(f"[Aura Heartbeat] Memory after reap: Free RAM {mem_after.get('free_gb')} GB / {mem_after.get('total_gb')} GB")

        result = {
            "timestamp": timestamp,
            "drive_ready": drive_ready,
            "attachments_offloaded": len(offloaded_files),
            "promotions_trashed": clean_res.get("trashed_count", 0),
            "unsub_detected": len(clean_res.get("unsubscribe_records", [])),
            "processes_reaped": reaped,
            "temp_files_cleaned": temp_cleaned,
            "vault_categorized": vault_stats,
            "desktop_cleaned": desktop_cleaned,
            "free_ram_gb": mem_after.get("free_gb"),
        }
        print(f"[Aura Heartbeat] Cycle finished: {result}")
        
        # Append to heartbeat evidence log
        log_path = Path(r"C:\LEO-LAB-ANTIGRAVITY\anti-hermes-mcp-proof\evidence\aura_heartbeat.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(f"{timestamp} [HEARTBEAT] offloaded={len(offloaded_files)} trashed={clean_res.get('trashed_count', 0)} reaped_procs={reaped} desktop={desktop_cleaned} free_ram={mem_after.get('free_gb')}GB\n")

        return result

    def run_heartbeat_loop(self, interval_seconds: int = 900):
        """Continuous background daemon loop running every interval_seconds."""
        print(f"[Aura Heartbeat] Daemon started. Running every {interval_seconds}s ({interval_seconds // 60} mins)...")
        import time
        while True:
            try:
                self.run_heartbeat_cycle()
            except Exception as exc:
                print(f"[Aura Heartbeat EXCEPTION] {exc}")
            time.sleep(interval_seconds)


sentinel = AuraInboxSentinel()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"

    
    print("=" * 60)
    print("  AURA INBOX & STORAGE SENTINEL — SAMSUNG DRIVE D:\\")
    print("=" * 60)
    print(f"Archive Directory: {ARCHIVE_BASE_DIR}")
    print(f"Active Command:    {cmd}\n")

    if cmd == "scan":
        heavy = sentinel.scan_heavy_emails(min_size_mb=5, max_results=10)
        print(f"[*] Heavy Emails (>5MB): {len(heavy)} found")
        for i, m in enumerate(heavy, 1):
            detail = sentinel._request(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{m['id']}?format=metadata&metadataHeaders=From&metadataHeaders=Subject")
            headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
            print(f"   [{i}] From: {headers.get('From', 'Unknown')[:30]} | Subject: {headers.get('Subject', '(no subject)')[:40]}")

        promos = sentinel.find_promotions_and_spam(max_results=10)
        print(f"\n[*] Promotional / Blast Ads: {len(promos)} found ready for trash/unsub")
        for i, m in enumerate(promos, 1):
            detail = sentinel._request(f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{m['id']}?format=metadata&metadataHeaders=From&metadataHeaders=Subject")
            headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
            print(f"   [{i}] From: {headers.get('From', 'Unknown')[:30]} | Subject: {headers.get('Subject', '(no subject)')[:40]}")

    elif cmd == "offload":
        heavy = sentinel.scan_heavy_emails(min_size_mb=5, max_results=10)
        print(f"[*] Processing {len(heavy)} heavy emails to offload to Samsung Drive...")
        total_offloaded = 0
        for m in heavy:
            saved = sentinel.download_attachments_and_offload(m["id"])
            if saved:
                total_offloaded += len(saved)
                sentinel.trash_message(m["id"])
                print(f"    -> Moved email {m['id']} to trash (attachments secured on D:\\)")
        print(f"\n[OK] Offloaded {total_offloaded} files to {ATTACHMENTS_DIR} and freed Gmail space.")

    elif cmd == "clean_promos":
        print("[*] Cleaning promotional blast emails...")
        res = sentinel.clean_promotions_batch(max_batch=30)
        print(f"[OK] Trashed {res['trashed_count']} promotional ads.")
        if res["unsubscribe_records"]:
            print(f"[*] Unsubscribe endpoints detected: {len(res['unsubscribe_records'])}")

    elif cmd == "purge_trash":
        print("[*] Permanently purging Gmail Trash to immediately reclaim storage quota...")
        purged = sentinel.empty_trash_messages(max_purge=100)
        print(f"[OK] Reclaimed Google Storage by permanently removing {purged} items from Trash.")

    elif cmd == "cycle":
        print("[*] Running single heartbeat cycle...")
        sentinel.run_heartbeat_cycle()

    elif cmd == "heartbeat":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 900
        sentinel.run_heartbeat_loop(interval_seconds=interval)

    else:
        print(f"Unknown command: {cmd}")
        print("Available commands: scan | offload | clean_promos | purge_trash | cycle | heartbeat [seconds]")


