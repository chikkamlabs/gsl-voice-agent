
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project directory
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")



def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()

    placeholders = {
        "SARVAM_API_KEY": "your_sarvam_api_key_here",
        "SARVAM_VOICE_ID": "your_chairman_voice_id",
    }

    if not value or value == placeholders.get(name):
        raise RuntimeError(
            f"Missing or placeholder configuration: {name}. "
            "Please check your .env file."
        )

    return value



SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "").strip()
SARVAM_VOICE_ID = os.getenv("SARVAM_VOICE_ID", "").strip()

SARVAM_LANGUAGE = os.getenv("SARVAM_LANGUAGE", "en-IN")

SARVAM_LLM_MODEL = os.getenv(
    "SARVAM_LLM_MODEL",
    "sarvam-105b-conversations",
)

SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v4")

SARVAM_TTS_MODEL = os.getenv("SARVAM_TTS_MODEL", "bulbul:v4-flash")

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))


def validate_sarvam_config() -> None:
    get_required_env("SARVAM_API_KEY")
