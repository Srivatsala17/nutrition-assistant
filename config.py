import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "chroma_db"
FOODS_CSV = "data/foods.csv"
LLM_MODEL = "openai/gpt-oss-120b"