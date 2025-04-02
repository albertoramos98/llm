import os
import model.model as model
from gpt4all import GPT4All
import streamlit as st
from database.database import query_database, buscar_resposta_cache, salvar_resposta
from cache.cache import get_database_schema
from config.config import MODEL_PATH

def generate_response(user_question):
    """Busca no cache ou gera uma nova resposta se necessário."""

    if model is None:
        return "❌ O modelo não foi carregado corretamente."

    if not user_question.strip():
        return "❌ Por favor, insira uma pergunta válida."

    # 🔥 Primeiro, verifica se a resposta já está no cache
    resposta_cache = buscar_resposta_cache(user_question)
    if resposta_cache:
        return f"📌 **Resposta recuperada do histórico:**\n\n{resposta_cache}"

    # 🔍 Obtém a estrutura do banco
    schema = get_database_schema()
    if not schema:
        return "❌ Erro ao buscar a estrutura do banco de dados."

    # Identificar a tabela mais relevante
    table_to_query = None
    for table in schema.keys():
        if table.lower() in user_question.lower():
            table_to_query = table
            break

    # Se nenhuma tabela for encontrada, listar as tabelas disponíveis
    if not table_to_query:
        return f"📊 O banco contém as seguintes tabelas:\n" + "\n".join([f"- {table}" for table in schema.keys()])

    # 🔍 Consulta otimizada (busca apenas colunas mais relevantes)
    columns = ", ".join(schema[table_to_query][:5])  # Limita a 5 colunas para otimizar
    query = f'SELECT {columns} FROM "{table_to_query}" ORDER BY ROWID DESC LIMIT 5;'
    result = query_database(query)

    if isinstance(result, str):
        return result  # Retorna erro de SQL, se houver

    # 🔥 Agora pedimos para a LLM interpretar os dados
    dados_texto = "\n".join([", ".join(map(str, row)) for row in result])
    prompt = f"""
    Você é um assistente que responde perguntas sobre um banco de dados.
    Aqui estão os últimos registros extraídos:

    {dados_texto}

    Com base nesses dados, responda à seguinte pergunta de forma clara e objetiva:
    "{user_question}"
    """

    try:
        resposta = model.generate(prompt).strip()
        

        # 🔥 Salvar resposta no cache para aprendizado futuro
        salvar_resposta(user_question, resposta)

        return resposta
    except Exception as e:
        return f"❌ Erro ao processar a solicitação: {str(e)}"


# 🧠 Cache do Modelo
@st.cache_resource
def load_model():
    """Carrega o modelo GPT4All apenas uma vez."""
    if not os.path.exists(MODEL_PATH):
        st.error(f"❌ Modelo não encontrado: {MODEL_PATH}")
        return None
    try:
        return GPT4All(MODEL_PATH)
    except Exception as e:
        st.error(f"❌ Erro ao carregar o modelo GPT4All: {str(e)}")
        return None

model = load_model()
if model:
    st.success("✅ Modelo carregado com sucesso!")