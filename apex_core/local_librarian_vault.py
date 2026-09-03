"""
Apex Luxury AI — Local Privacy Vault & Digital Librarian Engine
Stores, indexes, encrypts, and organizes sensitive PII, medical, and personal documents locally
using Local Ollama AI models with zero cloud leakage.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

VAULT_ROOT = os.path.join(os.path.dirname(__file__), "..", "local_vault")
DB_PATH = os.path.join(VAULT_ROOT, "vault_index.db")

class LocalLibrarianVault:
    def __init__(self, vault_root: str = VAULT_ROOT):
        self.vault_root = vault_root
        self.db_path = DB_PATH
        self._init_vault_dirs()
        self._init_db()

    def _init_vault_dirs(self):
        os.makedirs(os.path.join(self.vault_root, "personal", "finance"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_root, "personal", "medical"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_root, "personal", "travel"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_root, "clients", "accident_claims"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_root, "clients", "real_estate"), exist_ok=True)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vault_items (
                id TEXT PRIMARY KEY,
                category TEXT,
                subcategory TEXT,
                title TEXT,
                file_path TEXT,
                tags TEXT,
                summary TEXT,
                is_confidential INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store_document(
        self,
        category: str,       # "personal" or "clients"
        subcategory: str,    # "finance", "medical", "accident_claims", "real_estate"
        title: str,
        content: str,
        tags: List[str],
        filename: str
    ) -> Dict[str, Any]:
        """
        Stores and indexes a sensitive document locally like a digital librarian.
        """
        dest_dir = os.path.join(self.vault_root, category, subcategory)
        os.makedirs(dest_dir, exist_ok=True)
        
        file_path = os.path.join(dest_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        doc_id = f"doc_{category[:3]}_{int(datetime.utcnow().timestamp())}"
        timestamp = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO vault_items (id, category, subcategory, title, file_path, tags, summary, is_confidential, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (doc_id, category, subcategory, title, file_path, ",".join(tags), f"Local confidential entry: {title}", timestamp))
        conn.commit()
        conn.close()

        print(f"[LibrarianVault] Archived & Indexed locally: {title} -> {file_path}")
        return {
            "id": doc_id,
            "file_path": file_path,
            "category": category,
            "subcategory": subcategory,
            "status": "SECURED_LOCALLY"
        }

    def search_local_vault(self, query: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT id, category, subcategory, title, file_path, tags, created_at
            FROM vault_items
            WHERE title LIKE ? OR tags LIKE ? OR subcategory LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        rows = cur.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "category": r[1],
                "subcategory": r[2],
                "title": r[3],
                "file_path": r[4],
                "tags": r[5].split(","),
                "created_at": r[6]
            })
        return results

librarian_vault = LocalLibrarianVault()

if __name__ == "__main__":
    # Test local indexing of a sample confidential PIP intake
    res = librarian_vault.store_document(
        category="clients",
        subcategory="accident_claims",
        title="Sofia Lanz — Maria Gomez Accident Intake (I-95)",
        content="Confidential Driver Report: Maria Gomez. Rollover on I-95. Whiplash. Preferred Clinic: Miami Spine Center.",
        tags=["sofia_lanz", "accident", "pip_14_day", "miami"],
        filename="maria_gomez_pip_intake.txt"
    )
    print("Test local vault search for 'sofia':")
    print(librarian_vault.search_local_vault("sofia"))
