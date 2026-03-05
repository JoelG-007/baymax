import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "sqlite:///./baymax.db"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
