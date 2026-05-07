"""Environment configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "kitt_pfm.db"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env")

# Whisper
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Timezone
TZ = os.getenv("TZ", "Asia/Tokyo")

# MiniMax Vision API (for receipt OCR)
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
