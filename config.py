import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

LLM_API_KEY = os.getenv("LLM_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

LLM_MODEL = "openai/gpt-oss-120b"   # keep whichever model name worked for you

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = str(BASE_DIR / "chroma_db")
FOODS_CSV = str(BASE_DIR / "data" / "foods.csv")