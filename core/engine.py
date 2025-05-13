from core.llm_agent import generate_sql_with_memory, interpret
from core.database import run_query
from core.utils import list_tables, describe_table
from core.history import get_history
import re
import logging
from difflib import get_close_matches

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def is_interpretative(question: str) -> bool:
    keywords = [
        "importância", "significado", "impacto", "por que",
        "explique", "interprete", "contexto", "o que isso significa"
    ]
    return any(k in question.lower() for k in keywords)

def clean_query_output(sql: str) -> str:
    lines = sql.strip().splitlines()
    cleaned = [line for line in lines if not line.lower().startswith(("ai:", "resposta:", "sql:"))]
    return "\n".join(cleaned).strip()

def extract_identifiers(sql: str) -> list[str]:
    sql = re.sub(r"\s+AS\s+\w+", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"'[^']*'", "", sql)
    sql = re.sub(r'"[^"]*"', "", sql)
    return re.findall(r"\b\w+\b", sql)

def extract_aliases(sql: str) -> set[str]:
    return set(re.findall(r"\bAS\s+(\w+)", sql, flags=re.IGNORECASE))

def validate_columns_in_query(sql: str) -> tuple[list[str], set[str]]:
    identifiers = extract_identifiers(sql)
    aliases = extract_aliases(sql)
    sql_keywords = {
        "select", "from", "where", "group", "by", "order", "limit", "as",
        "and", "or", "not", "desc", "asc", "having", "between",
        "sum", "avg", "max", "min", "count", "distinct", "inner", "join", "on"
    }
    tables = list_tables()
    valid_columns = set()
    for table in tables:
        cols = describe_table(table)
        valid_columns.update({col for col, _ in cols})
        valid_columns.add(table)
    invalid = []
    for word in identifiers:
        if word.lower() in sql_keywords or word in valid_columns or word in aliases:
            continue
        if word.isdigit() or len(word) <= 2:
            continue
        if any(word.lower() == col.lower() for col in valid_columns):
            continue
        invalid.append(word)
    return invalid, valid_columns

def auto_correct_sql(sql: str, invalid_cols: list[str], valid_cols: set[str]) -> str:
    corrected_sql = sql
    for wrong in invalid_cols:
        suggestion = get_close_matches(wrong, valid_cols, n=1)
        if suggestion:
            corrected_sql = re.sub(rf"\b{re.escape(wrong)}\b", suggestion[0], corrected_sql)
            logger.info(f"[CORREÇÃO] Substituído: '{wrong}' → '{suggestion[0]}'")
    return corrected_sql

def is_valid_sql_structure(sql: str) -> bool:
    sql = sql.strip().lower()
    return sql.startswith("select") or sql.startswith("with")

def retrieve_last_sql_context() -> tuple[str, list[dict]]:
    history = get_history(limit=20)
    last_sql = next((h["content"] for h in reversed(history) if h["role"] == "assistant"), None)
    return last_sql, history

def auto_generate_and_run_query(question: str):
    if is_interpretative(question):
        last_sql, _ = retrieve_last_sql_context()
        if last_sql:
            try:
                result = run_query(last_sql)
                return {
                    "sql": last_sql,
                    "resultado": result,
                    "interpretacao": interpret(last_sql, result),
                    "tabela": "Consulta anterior reaproveitada"
                }
            except Exception as e:
                raise RuntimeError(f"Erro ao recuperar contexto anterior.\n\n{e}")
        else:
            raise RuntimeError("Não há contexto anterior suficiente para interpretar essa pergunta.")

    sql = generate_sql_with_memory(question)
    sql = clean_query_output(sql)

    if not is_valid_sql_structure(sql):
        raise RuntimeError(
            "A IA não conseguiu gerar uma consulta SQL válida para essa pergunta.\n"
            "Tente reformular sua pergunta, seja mais específico, ou verifique se os dados realmente existem.\n\n"
            f"Saída recebida:\n{sql}"
        )

    col_invalidas, col_validas = validate_columns_in_query(sql)

    if col_invalidas:
        logger.warning(f"[COLUNAS INVÁLIDAS] {col_invalidas}")
        sql_corrigido = auto_correct_sql(sql, col_invalidas, col_validas)

        col_invalidas_corrigidas, _ = validate_columns_in_query(sql_corrigido)
        if col_invalidas_corrigidas:
            raise RuntimeError(
                f"Não foi possível corrigir automaticamente as colunas inválidas: {', '.join(col_invalidas_corrigidas)}.\n"
                f"Query original:\n{sql}"
            )
        else:
            logger.info("[SQL CORRIGIDA] Correção automática bem-sucedida.")
            sql = sql_corrigido

    try:
        result = run_query(sql)
        logger.info(f"[EXEC SQL OK] {sql}")
        return {
            "sql": sql,
            "resultado": result,
            "interpretacao": interpret(sql, result),
            "tabela": "Detectada automaticamente"
        }
    except Exception as e:
        logger.error(f"[EXEC SQL ERRO] {sql} — {e}")
        raise RuntimeError(
            f"Erro ao executar a query (mesmo após tentativa de correção).\n\nSQL:\n{sql}\n\nDetalhes:\n{e}"
        )
