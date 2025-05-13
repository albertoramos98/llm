from __future__ import annotations

from langchain_community.utilities import SQLDatabase
from core.utils import DB_PATH, list_tables as _list_tables

_DB_URI = f"sqlite:///{DB_PATH}"
_db_inst: SQLDatabase | None = None

def get_db() -> SQLDatabase:
    global _db_inst
    if _db_inst is None:
        _db_inst = SQLDatabase.from_uri(_DB_URI, sample_rows_in_table_info=0)
    return _db_inst

def run_query(sql: str):
    return get_db().run(sql)

def list_tables() -> list[str]:
    return _list_tables()
