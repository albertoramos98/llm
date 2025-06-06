from core.engine import auto_generate_and_run_query


from core.llm_agent import get_answer_with_cache

def ask_question(question: str) -> str:
    return get_answer_with_cache(question)


def process_query(pergunta: str) -> dict:
    return auto_generate_and_run_query(pergunta)
