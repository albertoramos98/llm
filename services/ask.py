from core.engine import auto_generate_and_run_query

def process_query(pergunta: str) -> dict:
    return auto_generate_and_run_query(pergunta)
