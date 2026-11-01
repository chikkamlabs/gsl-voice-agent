from contextlib import asynccontextmanager

from fastapi import FastAPI

import config

import uuid
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Telugu AI Calling server starting...")
    print(f"Language: {config.SARVAM_LANGUAGE}")
    print(f"LLM model: {config.SARVAM_LLM_MODEL}")
    print(f"STT model: {config.SARVAM_STT_MODEL}")
    print(f"TTS model: {config.SARVAM_TTS_MODEL}")
    print(
        "Sarvam API key configured:",
        bool(config.SARVAM_API_KEY),
    )
    print(
        "Cloned voice ID configured:",
        bool(config.SARVAM_VOICE_ID),
    )

    yield

    print("Telugu AI Calling server stopped.")


app = FastAPI(
    title="Telugu AI Calling",
    description="Telugu AI voice assistant using Sarvam",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {
        "message": "Telugu AI Calling API is running",
        "stage": "initial_setup",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "sarvam_api_key_configured": bool(
            config.SARVAM_API_KEY
        ),
        "voice_id_configured": bool(
            config.SARVAM_VOICE_ID
        ),
        "language": config.SARVAM_LANGUAGE,
    }


@app.get("/config-status")
def config_status():
    # Never return API keys or other secrets.
    return {
        "llm_model": config.SARVAM_LLM_MODEL,
        "stt_model": config.SARVAM_STT_MODEL,
        "tts_model": config.SARVAM_TTS_MODEL,
        "language": config.SARVAM_LANGUAGE,
        "voice_id_configured": bool(config.SARVAM_VOICE_ID),
    }
