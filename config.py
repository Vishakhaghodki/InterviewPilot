import os
import secrets
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # If SECRET_KEY is not set, a random one is used (sessions reset on restart).
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    DATABASE = os.path.join(BASE_DIR, "instance", "interviewpilot.db")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB uploads
    SESSION_COOKIE_SAMESITE = "Lax"
    # AI settings come only from environment variables
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
    AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
