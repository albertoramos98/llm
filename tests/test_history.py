# 🔎 Testes para history.py
import sqlite3
from unittest.mock import patch
from core import history


# 🧪 Testa criação da tabela de histórico
def test_init_history_db_cria_tabela_temporaria(tmp_path):
    temp_db = tmp_path / "temp_history.db"

    with patch("core.history.HISTORY_DB", temp_db):
        history.init_history_db()

        with sqlite3.connect(temp_db) as conn:
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory';")
            assert result.fetchone() is not None


# 🧪 Testa inserção e recuperação de um item do histórico
def test_add_and_get_history(tmp_path):
    temp_db = tmp_path / "temp_history.db"

    with patch("core.history.HISTORY_DB", temp_db):
        history.init_history_db()
        history.add_to_history("user", "Qual a média de vendas?")
        history.add_to_history("assistant", "SELECT AVG(valor) FROM vendas")
        
        hist = history.get_history()
        assert len(hist) == 2
        assert hist[0]["role"] == "user"
        assert hist[1]["role"] == "assistant"
        assert "vendas" in hist[1]["content"]


# 🧪 Testa validação de role inválido
import pytest

def test_add_to_history_role_invalido(tmp_path):
    temp_db = tmp_path / "temp_history.db"

    with patch("core.history.HISTORY_DB", temp_db):
        history.init_history_db()
        with pytest.raises(ValueError):
            history.add_to_history("sistema", "isso deve falhar")
