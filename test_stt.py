
from stt import transcribe_audio

try:
    transcript = transcribe_audio("test_english.ogg")
    print("\nRecognised English text:")
    print(transcript)

except Exception as exc:
    print(f"\nSTT test failed: {exc}")
