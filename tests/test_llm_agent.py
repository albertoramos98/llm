import sys
from unittest.mock import MagicMock
import pytest
from unittest.mock import patch, MagicMock
sys.modules['langchain_ollama'] = MagicMock() 
#usado para rodar localmente

import sys
import os

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.llm_agent import (
    normalize_question,
    get_last_valid_sql,
    enrich_question,
    generate_sql,
    interpret,
    generate_sql_global,
    generate_sql_with_memory,
)

@pytest.mark.parametrize(
    "input_q, expected",
    [
        ("Qual a inflação?", "Qual a IPCA?"),
        ("inflação e aumento de preços", "IPCA e IPCA"),
        ("ocupação formal e empregados com carteira", "emprego formal e emprego formal"),
        ("sem substituição", "sem substituição"),
    ],
)
def test_normalize_question(input_q, expected):
    assert normalize_question(input_q) == expected

@patch("core.llm_agent.get_history")
def test_get_last_valid_sql(mock_get_history):
    mock_get_history.return_value = [
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "update tabela set x = 1"},
        {"role": "assistant", "content": "select * from tabela"},
        {"role": "assistant", "content": "WITH cte AS (SELECT 1) SELECT * FROM cte"},
        {"role": "user", "content": "Outra pergunta"},
    ]
    assert get_last_valid_sql() == "WITH cte AS (SELECT 1) SELECT * FROM cte"

@patch("core.llm_agent.get_history")
def test_get_last_valid_sql_no_sql(mock_get_history):
    mock_get_history.return_value = [
        {"role": "user", "content": "Oi"},
        {"role": "assistant", "content": "Comando update"},
    ]
    assert get_last_valid_sql() == ""

@pytest.mark.parametrize(
    "input_q, expected_contains",
    [
        ("Quero dados do IPCA Recife", "ipca_7060_recife"),
        ("IPCA Brasil", "tabelas que contêm 'brasil'"),
        ("Serviços no RN", "PMS é a Pesquisa Mensal de Serviços"),
        ("Consulta genérica", None),
    ],
)
def test_enrich_question(input_q, expected_contains):
    result = enrich_question(input_q)
    if expected_contains:
        assert expected_contains.lower() in result.lower()
    else:
        assert result == input_q

@patch("core.llm_agent._LLM.invoke")
def test_generate_sql(mock_invoke):
    mock_invoke.return_value = "SELECT * FROM tabela;"
    question = "Consulta"
    table = "tabela"
    sql = generate_sql(question, table)
    assert isinstance(sql, str)
    assert "SELECT" in sql.upper()

@patch("core.llm_agent._LLM.invoke")
def test_interpret(mock_invoke):
    mock_invoke.return_value = "Explicação clara do resultado."
    sql = "SELECT * FROM tabela"
    db_result = [{"col1": 1}]
    result = interpret(sql, db_result)
    assert "Explicação" in result or isinstance(result, str)

@patch("core.llm_agent._LLM.invoke")
def test_generate_sql_global(mock_invoke):
    mock_invoke.return_value = "SELECT * FROM todas_tabelas;"
    question = "Consulta global"
    sql = generate_sql_global(question)
    assert isinstance(sql, str)
    assert "SELECT" in sql.upper()

@patch("core.llm_agent._LLM.invoke")
@patch("core.llm_agent.get_history")
@patch("core.llm_agent.add_to_history")
def test_generate_sql_with_memory(
    mock_add_to_history, mock_get_history, mock_invoke
):
    mock_invoke.return_value = "SELECT * FROM tabela WHERE ano=2023;"
    mock_get_history.return_value = [
        {"role": "user", "content": "pergunta antiga"},
        {"role": "assistant", "content": "select * from tabela;"},
    ]
    question = "Qual a inflação no Brasil?"
    sql = generate_sql_with_memory(question)
    assert isinstance(sql, str)
    assert "SELECT" in sql.upper()
    mock_add_to_history.assert_any_call("user", question)
    mock_add_to_history.assert_any_call("assistant", sql)
