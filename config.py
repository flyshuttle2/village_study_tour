import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
BASE_URL = "https://api.minimaxi.com/v1"
LLM_MODEL = "MiniMax-M2.5"
IMAGE_MODEL = "image-01"
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

LOVART_ACCESS_KEY = os.getenv("LOVART_ACCESS_KEY", "")
LOVART_SECRET_KEY = os.getenv("LOVART_SECRET_KEY", "")
LOVART_AVAILABLE = bool(LOVART_ACCESS_KEY and LOVART_SECRET_KEY)
