import os

from dotenv import load_dotenv

load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODELO_GROQ = os.getenv("MODELO_GROQ", "openai/gpt-oss-120b")
PORTA = int(os.getenv("PORT", "7862"))
