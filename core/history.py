import sqlite3
from pathlib import Path
from typing import List, Dict

HISTORY_DB = Path("hubia_history.db")
HISTORY_DB.parent.mkdir(parents=True, exist_ok=True)

def init_history_db():
    with sqlite3.connect(HISTORY_DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

def add_to_history(role: str, content: str):
    if role not in ("user", "assistant"):
        raise ValueError("O role deve ser 'user' ou 'assistant'.")
    with sqlite3.connect(HISTORY_DB) as conn:
        conn.execute("INSERT INTO memory (role, content) VALUES (?, ?)", (role, content))

def get_history(limit: int = 10) -> List[Dict[str, str]]:
    with sqlite3.connect(HISTORY_DB) as conn:
        rows = conn.execute(
            "SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
