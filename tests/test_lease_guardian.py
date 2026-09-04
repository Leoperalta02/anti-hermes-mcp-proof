import os
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from apex_core.lease_guardian import purge_stale_leases, run_guardian_cycle


class TestLeaseGuardian(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_state.db"

        # Initialize schema matching Hermes session_turn_leases
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("""
            CREATE TABLE session_turn_leases (
                session_id TEXT PRIMARY KEY,
                holder TEXT NOT NULL,
                acquired_at REAL NOT NULL,
                expires_at REAL NOT NULL
            );
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_purge_stale_leases_only_deletes_expired(self):
        now = 1000.0
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        # Stale lease 1 (expired at 950)
        c.execute("INSERT INTO session_turn_leases VALUES ('s1', 'worker1', 900.0, 950.0);")
        # Stale lease 2 (expired at 999.9)
        c.execute("INSERT INTO session_turn_leases VALUES ('s2', 'worker2', 910.0, 999.9);")
        # Active lease (expires at 1050)
        c.execute("INSERT INTO session_turn_leases VALUES ('s3', 'worker3', 990.0, 1050.0);")
        conn.commit()
        conn.close()

        purged = purge_stale_leases(db_path=self.db_path, now=now)
        self.assertEqual(purged, 2)

        # Verify remaining
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        c.execute("SELECT session_id FROM session_turn_leases;")
        rows = c.fetchall()
        conn.close()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "s3")

    def test_purge_stale_leases_handles_missing_table_gracefully(self):
        empty_db = Path(self.temp_dir.name) / "empty.db"
        conn = sqlite3.connect(str(empty_db))
        conn.close()

        purged = purge_stale_leases(db_path=empty_db)
        self.assertEqual(purged, 0)


if __name__ == "__main__":
    unittest.main()
