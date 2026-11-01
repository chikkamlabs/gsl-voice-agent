
# stt.py

from pathlib import Path

from sarvamai import SarvamAI

import config


def transcribe_audio(audio_path: str | Path) -> str:
    """
    Convert an English audio recording into text.

    Supported input formats include WAV and MP3.
    For the first test, use a short English WAV recording.
    """
    path = Path(audio_path)

    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")

    client = SarvamAI(
        api_subscription_key=config.get_required_env(
            "SARVAM_API_KEY"
        )
    )

    try:
        with path.open("rb") as audio_file:
            response = client.speech_to_text.transcribe(
                file=audio_file,
                model=config.SARVAM_STT_MODEL,
                mode="transcribe",
                language_code=config.SARVAM_LANGUAGE,
            )

        transcript = (response.transcript or "").strip()

        if not transcript:
            raise RuntimeError(
                "Sarvam returned an empty transcription."
            )

        return transcript

    except Exception as exc:
        raise RuntimeError(
            f"Sarvam STT failed: {exc}"
        ) from exc
