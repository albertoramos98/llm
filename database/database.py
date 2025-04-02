import sqlite3
from config.config import DB_PATH, CACHE_DB_PATH


def query_database(query):
    """Executa uma consulta no banco de dados SQLite."""
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)  # Apenas leitura
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except sqlite3.Error as e:
        return f"❌ Erro ao executar a consulta: {str(e)}"


def salvar_resposta(pergunta, resposta):
    """Armazena a pergunta e resposta no cache para aprendizado futuro."""
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO historico (pergunta, resposta) VALUES (?, ?)", (pergunta, resposta))
    conn.commit()
    conn.close()


def buscar_resposta_cache(pergunta):
    """Verifica se já existe uma resposta no cache."""
    conn = sqlite3.connect(CACHE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT resposta FROM historico WHERE pergunta = ?", (pergunta,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None


