import os
from dotenv import load_dotenv

# 📌 Carregar configurações do `.env`
load_dotenv()

modelo_path = os.getenv(
    "MODEL_PATH", 
    "~/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
)
