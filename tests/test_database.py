import pytest
from unittest.mock import patch, MagicMock
from core import database

##get_db()	Verifica que a instância é singleton e criada só 1x com from_uri

def test_get_db_singleton():
    with patch('core.database.SQLDatabase.from_uri') as mock_from_uri:
        mock_instance = MagicMock()
        mock_from_uri.return_value = mock_instance

        # Força a variável global a None para simular primeiro uso
        database._db_inst = None
        db1 = database.get_db()
        db2 = database.get_db()

        assert db1 is db2
        assert mock_from_uri.call_count == 1

##run_query()	Garante que a query é executada usando o mock do get_db()
def test_run_query():
    mock_db = MagicMock()
    mock_db.run.return_value = "resultado_fake"

    with patch('core.database.get_db', return_value=mock_db):
        result = database.run_query("SELECT * FROM teste")
        assert result == "resultado_fake"
        mock_db.run.assert_called_once_with("SELECT * FROM teste")

##list_tables()	Testa que está chamando o _list_tables() corretamente (mockado)
def test_list_tables():
    with patch('core.database._list_tables', return_value=["tabela1", "tabela2"]):
        result = database.list_tables()
        assert result == ["tabela1", "tabela2"]



