import sys
from unittest.mock import MagicMock
sys.modules['langchain_ollama'] = MagicMock()
import pytest
from core.engine import is_interpretative, clean_query_output, is_valid_sql_structure


def test_is_interpretative_true():
    pergunta = "Qual o impacto do aquecimento global?"
    assert is_interpretative(pergunta) is True


def test_is_interpretative_false():
    pergunta = "Me mostre os dados da tabela de vendas"
    assert is_interpretative(pergunta) is False

def test_clean_query_output_remove_prefixos():
    sql = "AI: SELECT * FROM tabela\nResposta: Isso é um teste\nSQL: SELECT nome FROM pessoas"
    esperado = ""  # todas as linhas removidas!
    resultado = clean_query_output(sql)
    assert resultado == esperado



def test_is_valid_sql_structure_true():
    assert is_valid_sql_structure("SELECT * FROM produtos") is True
    assert is_valid_sql_structure("  WITH cte AS (...) SELECT * FROM cte") is True


def test_is_valid_sql_structure_false():
    assert is_valid_sql_structure("DELETE FROM usuarios") is False
    assert is_valid_sql_structure("insira dados aqui") is False

# 🔎 Testes para extract_identifiers()
from core.engine import extract_identifiers, extract_aliases

def test_extract_identifiers_simples():
    # Deve extrair corretamente os identificadores de uma query básica
    sql = "SELECT nome, idade FROM pessoas WHERE idade > 18"
    resultado = extract_identifiers(sql)
    assert set(resultado) >= {"nome", "idade", "pessoas"}


def test_extract_identifiers_ignora_literals_e_alias():
    # Deve ignorar strings literais e aliases
    sql = "SELECT nome AS n, idade FROM pessoas WHERE cidade = 'Recife'"
    resultado = extract_identifiers(sql)
    assert "Recife" not in resultado
    assert "n" not in resultado
    assert "nome" in resultado
    assert "idade" in resultado
    assert "pessoas" in resultado


# 🔎 Testes para extract_aliases()
def test_extract_aliases_simples():
    # Deve extrair corretamente aliases definidos com AS
    sql = "SELECT nome AS n, idade AS i FROM pessoas"
    resultado = extract_aliases(sql)
    assert resultado == {"n", "i"}


def test_extract_aliases_case_insensitive():
    # Deve reconhecer aliases mesmo com 'as' minúsculo
    sql = "SELECT nome as NomeColuna FROM usuarios"
    resultado = extract_aliases(sql)
    assert "NomeColuna" in resultado


# 🔎 Testes para validate_columns_in_query()
from core.engine import validate_columns_in_query
from unittest.mock import patch

def test_validate_columns_all_valid():
    # Tudo que está na SQL existe no banco → nenhuma coluna inválida
    sql = "SELECT nome, idade FROM clientes"

    with patch("core.engine.list_tables", return_value=["clientes"]), \
         patch("core.engine.describe_table", return_value=[("nome", "TEXT"), ("idade", "INTEGER")]):
        
        col_invalidas, col_validas = validate_columns_in_query(sql)
        assert col_invalidas == []
        assert "nome" in col_validas
        assert "clientes" in col_validas


def test_validate_columns_com_invalida():
    # A SQL inclui uma coluna que não existe → deve retornar como inválida
    sql = "SELECT nome, fruta_exotica FROM clientes"

    with patch("core.engine.list_tables", return_value=["clientes"]), \
         patch("core.engine.describe_table", return_value=[("nome", "TEXT"), ("idade", "INTEGER")]):
        
        col_invalidas, col_validas = validate_columns_in_query(sql)
        assert "fruta_exotica" in col_invalidas
        assert "nome" in col_validas

# 🔎 Teste para retrieve_last_sql_context()
from core.engine import retrieve_last_sql_context

def test_retrieve_last_sql_context_recupera_sql():
    mock_history = [
        {"role": "user", "content": "Qual a média?"},
        {"role": "assistant", "content": "SELECT AVG(valor) FROM tabela"},
    ]

    with patch("core.engine.get_history", return_value=mock_history):
        sql, hist = retrieve_last_sql_context()
        assert sql == "SELECT AVG(valor) FROM tabela"
        assert hist == mock_history

# 🔎 Teste para auto_generate_and_run_query() — caminho interpretativo
from core.engine import auto_generate_and_run_query

def test_auto_generate_and_run_query_interpretativo():
    pergunta = "Qual a importância do produto X?"

    with patch("core.engine.is_interpretative", return_value=True), \
         patch("core.engine.get_history", return_value=[
             {"role": "assistant", "content": "SELECT * FROM vendas"}
         ]), \
         patch("core.engine.run_query", return_value=[{"produto": "X", "quantidade": 10}]), \
         patch("core.engine.interpret", return_value="O produto X teve destaque nas vendas"):

        resultado = auto_generate_and_run_query(pergunta)

        assert resultado["sql"] == "SELECT * FROM vendas"
        assert resultado["resultado"] == [{"produto": "X", "quantidade": 10}]
        assert resultado["interpretacao"] == "O produto X teve destaque nas vendas"
        assert resultado["tabela"] == "Consulta anterior reaproveitada"
