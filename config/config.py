from dotenv import load_dotenv
import os

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4-mini")
DB_PATH = os.getenv("DB_PATH", "fecomdb.db")
