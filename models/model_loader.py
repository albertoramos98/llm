from config.config import OLLAMA_MODEL
import ollama  # ou qualquer lib de interface

def load_model():
    try:
        return ollama.Chat(model=OLLAMA_MODEL)
    except Exception as e:
        print(f"Erro ao carregar modelo: {e}")
        return None
