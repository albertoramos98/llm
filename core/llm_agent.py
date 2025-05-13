from __future__ import annotations

from functools import lru_cache
from typing import Any
import logging
from langchain_ollama import OllamaLLM

from core.prompts import make_system_prompt, make_system_prompt_all, INTERPRET_SYSTEM_PROMPT
from core.utils import strip_sql_markup
from core.history import get_history, add_to_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_LLM = OllamaLLM(model="phi4-mini")

def normalize_question(q: str) -> str:
    replacements = {
        "inflação": "IPCA",
        "índice de preços": "IPCA",
        "índice de preço": "IPCA",
        "preço ao consumidor": "IPCA",
        "aumento de preços": "IPCA",
        "custo de vida": "IPCA",
        "ocupação formal": "emprego formal",
        "empregados com carteira": "emprego formal"
    }
    for k, v in replacements.items():
        q = q.replace(k, v)
    return q

def get_last_valid_sql() -> str:
    history = get_history(limit=20)
    for entry in reversed(history):
        if entry['role'] == 'assistant' and entry['content'].lower().startswith(('select', 'with')):
            return entry['content']
    return ""

def enrich_question(q: str) -> str:
    lower_q = q.lower()
    hints = []

    if "recife" in lower_q and "ipca" in lower_q:
        hints.append("Nota: a tabela `ipca_7060_recife` contém dados do IPCA da cidade do Recife.")
    if "brasil" in lower_q and "ipca" in lower_q:
        hints.append("Nota: use as tabelas que contêm 'brasil' no nome para dados nacionais do IPCA.")
    if "serviços" in lower_q and "rn" in lower_q:
        hints.append("Nota: PMS é a Pesquisa Mensal de Serviços, representando o volume de serviços por setor no RN.")

    enriched = q
    if hints:
        enriched += "\n\n" + "\n".join(hints)

    return enriched

@lru_cache(maxsize=64)
def generate_sql(question: str, table: str) -> str:
    messages = [
        {"role": "system", "content": make_system_prompt(table)},
        {"role": "user", "content": question},
    ]
    raw = _LLM.invoke(messages)
    return strip_sql_markup(raw)

@lru_cache(maxsize=64)
def interpret(sql: str, db_result: Any) -> str:
    resumo_prompt = (
        f"Resultado da consulta SQL: {db_result}\nQuery executada: {sql}\n\n"
        "Explique o resultado de forma clara e formal, sem redundância."
    )
    messages = [
        {"role": "system", "content": INTERPRET_SYSTEM_PROMPT},
        {"role": "user", "content": resumo_prompt},
    ]
    return _LLM.invoke(messages)

@lru_cache(maxsize=64)
def generate_sql_global(question: str) -> str:
    messages = [
        {"role": "system", "content": make_system_prompt_all()},
        {"role": "user", "content": question},
    ]
    raw = _LLM.invoke(messages)
    return strip_sql_markup(raw)

def generate_sql_with_memory(question: str) -> str:
    cleaned = normalize_question(question)
    enriched = enrich_question(cleaned)

    messages = [{"role": "system", "content": make_system_prompt_all()}]
    messages += get_history(limit=10)
    messages.append({"role": "user", "content": enriched})

    raw = _LLM.invoke(messages)
    sql = strip_sql_markup(raw)

    logger.info(f"[Pergunta] {question}")
    logger.info(f"[Pergunta enriquecida] {enriched}")
    logger.info(f"[SQL gerada] {sql}")

    add_to_history("user", question)
    add_to_history("assistant", sql)

    return sql
