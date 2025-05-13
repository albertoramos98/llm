from __future__ import annotations

import os
import re
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

SQL_CODE_BLOCK = re.compile(r"```sql(.*?)```", re.S | re.I)

@lru_cache(maxsize=128)
def strip_sql_markup(text: str) -> str:
    m = SQL_CODE_BLOCK.search(text)
    return (m.group(1) if m else text).strip()

DB_PATH = Path(os.getenv("HUBIA_DB", "fecomdb.db"))
if not DB_PATH.exists():
    raise FileNotFoundError(
        f"Banco de dados não encontrado em: {DB_PATH.resolve()}\n"
        f"Dica: defina a variável de ambiente HUBIA_DB com o caminho correto."
    )

@lru_cache(maxsize=32)
def describe_table(table: str) -> List[Tuple[str, str]]:
    if not re.fullmatch(r"[\w\d_]+", table):
        raise ValueError(f"Nome de tabela inválido: {table}")
    with sqlite3.connect(str(DB_PATH)) as conn:
        rows = conn.execute(f'PRAGMA table_info("{table}");').fetchall()
    return [(r[1], r[2].upper()) for r in rows]

@lru_cache(maxsize=8)
def list_tables() -> List[str]:
    with sqlite3.connect(str(DB_PATH)) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchall()
    return [r[0] for r in rows]
