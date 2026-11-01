
# tts.py

import base64
from pathlib import Path

from sarvamai import SarvamAI

import config


def generate_speech(
    text: str,
    output_path: str | Path = "output.wav",
) -> str:
    """Generate Telugu audio using the saved cloned voice."""

    text = text.strip()

    if not text:
        raise ValueError("Text cannot be empty.")

    if len(text) > 1000:
        raise ValueError(
            "Text exceeds 1000 characters. "
            "Split longer answers into smaller sections."
        )

    voice_id = config.SARVAM_VOICE_ID.strip()

    if not voice_id:
        raise RuntimeError(
            "SARVAM_VOICE_ID is missing from your .env file. "
            "Create the authorised voice clone first."
        )

    client = SarvamAI(
        api_subscription_key=config.get_required_env(
            "SARVAM_API_KEY"
        )
    )

    try:
        response = client.voice_cloning.convert(
            voice_id=voice_id,
            text=text,
            language_code=config.SARVAM_LANGUAGE,
        )

        audio_b64 = (
    getattr(response, "audio_b64", None)
    or getattr(response, "audio", None)
)

        if not audio_b64:
            raise RuntimeError(
                "Sarvam did not return audio data."
            )

        audio_bytes = base64.b64decode(audio_b64)

        destination = Path(output_path)
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        destination.write_bytes(audio_bytes)

        return str(destination.resolve())

    except Exception as exc:
        raise RuntimeError(
            f"Sarvam cloned-voice TTS failed: {exc}"
        ) from exc
