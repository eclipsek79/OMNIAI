"""
SQLite-backed simple memory store.

Table:
memory(
  id INTEGER PRIMARY KEY,
  goal TEXT,
  step TEXT,
  result TEXT
)
"""
from __future__ import annotations
import sqlite3
import threading
import os
from typing import List, Dict

from . import config, utils

logger = utils.logger

_lock = threading.Lock()

def _ensure_db():
    db_path = config.DATABASE_PATH
    dirpath = os.path.dirname(db_path) or "."
    if not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal TEXT,
        step TEXT,
        result TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def save_entry(goal: str, step: str, result: str) -> None:
    """Persist a step/result pair for a goal."""
    _ensure_db()
    with _lock:
        conn = sqlite3.connect(config.DATABASE_PATH, timeout=10)
        cur = conn.cursor()
        cur.execute("INSERT INTO memory (goal, step, result) VALUES (?, ?, ?)", (goal, step, result))
        conn.commit()
        conn.close()
    logger.debug("Saved memory entry: %s / %s", step, result)

def load_last(n: int = 20) -> List[Dict[str, str]]:
    """Load last n memory entries ordered by newest first."""
    _ensure_db()
    conn = sqlite3.connect(config.DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, goal, step, result, created_at FROM memory ORDER BY id DESC LIMIT ?", (n,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
