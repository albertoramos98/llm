from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Any

from langchain_ollama import OllamaLLM

from core.prompts import make_system_prompt, make_system_prompt_all, INTERPRET_SYSTEM_PROMPT
from core.utils import strip_sql_markup

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_LLM = OllamaLLM(model="phi4-mini")


def normalize_question(q: str) -> str:
    replacements = {
        r"\binflação\b": "IPCA",
        r"\bíndice de preços?\b": "IPCA",
        r"\bpreço ao consumidor\b": "IPCA",
        r"\baumento de preços\b": "IPCA",
        r"\bcusto de vida\b": "IPCA",
        r"\bocupação formal\b": "emprego formal",
        r"\bempregados com carteira\b": "emprego formal"
    }
    for pattern, replacement in replacements.items():
        q = re.sub(pattern, replacement, q, flags=re.IGNORECASE)
    return q


def enrich_question(q: str) -> str:
    lower_q = q.lower()
    hints = []

    if "recife" in lower_q and "ipca" in lower_q:
        hints.append("Nota: a tabela `ipca_7060_recife` contém dados do IPCA da cidade do Recife.")
    if "brasil" in lower_q and "ipca" in lower_q:
        hints.append("Nota: use as tabelas que contêm 'brasil' no nome para dados nacionais do IPCA.")
    if "serviços" in lower_q and "rn" in lower_q:
        hints.append("Nota: PMS é a Pesquisa Mensal de Serviços, representando o volume de serviços por setor no RN.")

    return q + ("\n\n" + "\n".join(hints) if hints else "")


@lru_cache(maxsize=64)
def generate_sql(question: str, table: str) -> str:
    messages = [
        {"role": "system", "content": make_system_prompt(table)},
        {"role": "user", "content": question},
    ]
    raw = _LLM.invoke(messages)
    return strip_sql_markup(raw)

def interpret(sql: str, db_result: Any) -> str:
    resumo_prompt = (
        f"Resultado da consulta SQL: {db_result}\n"
        f"Query executada: {sql}\n\n"
        "Explique o resultado de forma clara e formal, sem redundância."
    )
    messages = [
        {"role": "system", "content": INTERPRET_SYSTEM_PROMPT},
        {"role": "user", "content": resumo_prompt},
    ]
    return _LLM.invoke(messages)


def generate_sql_with_memory(question: str) -> str:
    cleaned = normalize_question(question)
    enriched = enrich_question(cleaned)

    messages = [{"role": "system", "content": make_system_prompt_all()}]
    messages.append({"role": "user", "content": enriched})

    raw = _LLM.invoke(messages)
    sql = strip_sql_markup(raw)

    logger.info(f"[Pergunta original] {question}")
    logger.info(f"[Pergunta enriquecida] {enriched}")
    logger.info(f"[SQL gerada] {sql}")

    return sql
