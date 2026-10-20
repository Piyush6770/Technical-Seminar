"""
Local Disk / SQLite Caching for Extracted Journal Features
"""

import sqlite3
import json
import os
import hashlib
from typing import Dict, Any, Optional
from src.config import FEATURE_CACHE_PATH

class FeatureCache:
    def __init__(self, db_path: str = FEATURE_CACHE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feature_cache (
                    cache_key TEXT PRIMARY KEY,
                    stage_name TEXT,
                    features_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def generate_key(url: str, journal_name: str, stage: str) -> str:
        raw = f"{stage}|{url or ''}|{journal_name or ''}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT features_json FROM feature_cache WHERE cache_key = ?", (cache_key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return None
        return None

    def set(self, cache_key: str, stage_name: str, features: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO feature_cache (cache_key, stage_name, features_json)
                VALUES (?, ?, ?)
            """, (cache_key, stage_name, json.dumps(features)))
            conn.commit()

# Global default instance
default_cache = FeatureCache()
