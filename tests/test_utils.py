import sqlite3
import tempfile
from pathlib import Path
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import strip_sql_markup, describe_table, list_tables, DB_PATH

@pytest.fixture
def test_db(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd) 

    monkeypatch.setenv("HUBIA_DB", path)

    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL
        );
    """)
    conn.commit()
    conn.close()

    yield Path(path)

    try:
        os.remove(path)
    except PermissionError:
        import time
        time.sleep(0.1)
        try:
            os.remove(path)
        except Exception as e:
            print(f"⚠️ Erro ao remover o arquivo temporário: {e}")

def test_strip_sql_markup():
    text = "```sql\nSELECT * FROM produtos;\n```"
    assert strip_sql_markup(text) == "SELECT * FROM produtos;"

def test_strip_sql_markup_without_code_block():
    text = "SELECT * FROM produtos;"
    assert strip_sql_markup(text) == "SELECT * FROM produtos;"

def test_list_tables(test_db, monkeypatch):
    monkeypatch.setattr("core.utils.DB_PATH", test_db)
    tables = list_tables()
    assert "produtos" in tables

def test_describe_table(test_db, monkeypatch):
    monkeypatch.setattr("core.utils.DB_PATH", test_db)
    cols = describe_table("produtos")
    assert ("id", "INTEGER") in cols
    assert ("nome", "TEXT") in cols
    assert ("preco", "REAL") in cols
