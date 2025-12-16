import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH: Path = Path(__file__).resolve().parent / "tracked.db"

def get_conn() -> sqlite3.Connection:
    conn: sqlite3.Connection = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn: sqlite3.Connection = get_conn()
    c: sqlite3.Cursor = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS tracked (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking TEXT NOT NULL UNIQUE,
            label TEXT,
            last_result TEXT,
            last_checked TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    # If the column 'label' was added after table creation in older DBs,
    # ensure it exists (SQLite ignores ADD COLUMN if exists, so we guard)
    try:
        c.execute("SELECT label FROM tracked LIMIT 1")
    except sqlite3.OperationalError:
        # Column missing; add it
        c.execute("ALTER TABLE tracked ADD COLUMN label TEXT")
    conn.commit()
    conn.close()

def list_tracked():
    conn: sqlite3.Connection = get_conn()
    c: sqlite3.Cursor = conn.cursor()
    c.execute("SELECT id, tracking, label, last_result, last_checked, created_at FROM tracked ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    out = []
    for r in rows:
        # r indices: 0=id,1=tracking,2=label,3=last_result,4=last_checked,5=created_at
        label = r[2]
        lr_raw = r[3]
        try:
            lr: sqlite3.Any | None = json.loads(lr_raw) if lr_raw else None
        except Exception:
            lr = None
        out.append({
            "id": r[0],
            "tracking": r[1],
            "label": label,
            "last_result": lr,
            "last_checked": r[4],
            "created_at": r[5],
        })
    return out

def add_tracked(tracking, label=None) -> int | None:
    conn: sqlite3.Connection = get_conn()
    c: sqlite3.Cursor = conn.cursor()
    now: str = datetime.utcnow().isoformat()
    try:
        c.execute("INSERT INTO tracked (tracking, label, created_at) VALUES (?, ?, ?)", (tracking, label, now))
        conn.commit()
        rowid: int | None = c.lastrowid
    except sqlite3.IntegrityError:
        # already exists
        rowid = None
    conn.close()
    return rowid


def update_tracked_label(item_id, label) -> bool:
    conn: sqlite3.Connection = get_conn()
    c: sqlite3.Cursor = conn.cursor()
    c.execute("UPDATE tracked SET label=? WHERE id=?", (label, item_id))
    conn.commit()
    updated: int = c.rowcount
    conn.close()
    return updated > 0

def remove_tracked(item_id) -> bool:
    conn: sqlite3.Connection = get_conn()
    c: sqlite3.Cursor = conn.cursor()
    c.execute("DELETE FROM tracked WHERE id=?", (item_id,))
    conn.commit()
    deleted: int = c.rowcount
    conn.close()
    return deleted > 0

def update_tracked_result(item_id, result) -> None:
    conn: sqlite3.Connection = get_conn()
    c: sqlite3.Cursor = conn.cursor()
    now: str = datetime.utcnow().isoformat()
    c.execute("UPDATE tracked SET last_result=?, last_checked=? WHERE id=?", (json.dumps(result, ensure_ascii=False), now, item_id))
    conn.commit()
    conn.close()
