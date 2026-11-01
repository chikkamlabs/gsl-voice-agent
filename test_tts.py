
from pathlib import Path
from tts import generate_speech

test_text = (
    "Hi, I am Gganni Bhaskar rao. I am a robotic surgeon and chairman of gsl Medical College and vice President for central zone of IAGS. Now, I am participating for president of IAGS in coming 2027-2028 term. Please vote for me in Jan 2027 Elections")

try:
    output_file = generate_speech(
        text=test_text,
        output_path="chairman_intro.wav",
    )

    print("TTS test successful!")
    print(f"Audio saved to: {output_file}")
    print("Play the audio and check the voice quality.")

except Exception as exc:
    print(f"TTS test failed: {exc}")
