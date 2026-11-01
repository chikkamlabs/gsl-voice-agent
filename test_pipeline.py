
from pathlib import Path
from uuid import uuid4
import threading
import time
import wave

import sounddevice as sd
import soundfile as sf
import webrtcvad

from stt import transcribe_audio
from llm import generate_answer, generate_call_analysis
from tts import generate_speech
from conversations import (
    start_conversation,
    get_history,
    add_message,
    save_call_analysis
)

# ---------- Configuration ----------

BASE_DIR = Path(__file__).resolve().parent

INTRO_FILE = BASE_DIR / "chairman_intro.wav"
INPUT_FILE = BASE_DIR / "test.wav"
OUTPUT_FILE = BASE_DIR / "output.wav"

CONVERSATION_ID = f"conversation_{uuid4().hex[:8]}"

SAMPLE_RATE = 16000

MAX_RECORD_SECONDS = 10
SILENCE_SECONDS = 2
VAD_FRAME_MS = 30

MAX_NO_RESPONSE = 2

INTRO_TEXT = """
Hi, I am Gganni Bhaskar rao.
I am a robotic surgeon, chairman of GSL Medical College
and vice President for central zone of IAGS.
Now, I am participating for president of IAGS
in coming 2027-2028 term.
Please vote for me in Jan 2027 Elections.
"""

# ---------- Keyboard Controls ----------

stop_playback = threading.Event()
quit_requested = threading.Event()
is_playing = threading.Event()


def keyboard_listener():

    while not quit_requested.is_set():

        command = input(
            "\nPress Enter to interrupt, or type q to quit: "
        ).strip().lower()

        if command == "q":
            quit_requested.set()
            stop_playback.set()
            break

        if is_playing.is_set():
            stop_playback.set()


# ---------- Audio Recording with VAD ----------

def record_from_microphone():

    if quit_requested.is_set():
        return False

    vad = webrtcvad.Vad(2)

    frame_samples = int(
        SAMPLE_RATE * VAD_FRAME_MS / 1000
    )

    silence_limit = int(
        SILENCE_SECONDS * 1000 / VAD_FRAME_MS
    )

    max_frames = int(
        MAX_RECORD_SECONDS * 1000 / VAD_FRAME_MS
    )

    audio_frames = []

    speech_detected = False
    silence_count = 0

    print("\nListening... Speak now.")
    print(f"Maximum speaking time: {MAX_RECORD_SECONDS} seconds")
    print(f"Recording stops after {SILENCE_SECONDS} seconds of silence.")

    try:

        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=frame_samples,
            channels=1,
            dtype="int16",
        ) as stream:

            for _ in range(max_frames):

                if quit_requested.is_set():
                    return False

                audio_data, overflowed = stream.read(frame_samples)

                audio_bytes = bytes(audio_data)

                is_speech = vad.is_speech(
                    audio_bytes,
                    SAMPLE_RATE,
                )

                audio_frames.append(audio_bytes)

                if is_speech:

                    if not speech_detected:
                        print("\nSpeech detected...")

                    speech_detected = True
                    silence_count = 0

                elif speech_detected:

                    silence_count += 1

                    if silence_count >= silence_limit:
                        print("\n3 seconds of silence detected.")
                        break

        if not speech_detected:
            print("\nNo speech detected.")
            return False

        # Save recorded audio as WAV.
        with wave.open(str(INPUT_FILE), "wb") as wav_file:

            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(b"".join(audio_frames))

        print("\nRecording completed.")
        return True

    except Exception as exc:

        print(f"\nRecording error: {exc}")
        raise


# ---------- Audio Playback ----------

def play_audio_with_interrupt(audio_file):

    audio, sample_rate = sf.read(
        str(audio_file),
        dtype="float32",
        always_2d=True,
    )

    chunk_size = 1024

    print("\nAssistant is speaking...")

    stop_playback.clear()
    is_playing.set()

    try:

        with sd.OutputStream(
            samplerate=sample_rate,
            channels=audio.shape[1],
            dtype="float32",
        ) as stream:

            for start in range(0, len(audio), chunk_size):

                if quit_requested.is_set():
                    stream.abort()
                    return "quit"

                if stop_playback.is_set():
                    stream.abort()
                    print("\nAssistant interrupted. Your turn!")
                    return "interrupted"

                chunk = audio[start:start + chunk_size]
                stream.write(chunk)

        print("\nAssistant finished speaking.")
        return "finished"

    finally:

        is_playing.clear()
        stop_playback.clear()
        sd.stop()


def play_fallback_message(message):

    if quit_requested.is_set():
        return "quit"

    print(f"\nAssistant: {message}")

    audio_file = generate_speech(
        message,
        output_path=OUTPUT_FILE,
    )

    return play_audio_with_interrupt(audio_file)

def analyse_completed_call():

    print("\nGenerating final call analysis...")

    try:
        # Get all messages from this conversation.
        final_history = get_history(CONVERSATION_ID)

        # Ask Sarvam LLM to analyse the conversation.
        analysis = generate_call_analysis(final_history)

        # Save analysis in conversation_history.json.
        save_call_analysis(
            CONVERSATION_ID,
            analysis,
        )

        print("\nCall analysis saved successfully.")

        print(f"\nSummary: {analysis['summary']}")
        print(f"Interest Score: {analysis['interest_score']}/100")
        print(f"Need Human: {analysis['need_human']}")
        print(f"Call Again: {analysis['call_again']}")

    except Exception as exc:
        print(f"\nCould not generate call analysis: {exc}")

# ---------- Conversation ----------

def main():

    if not INTRO_FILE.is_file():
        print(f"Introduction audio not found: {INTRO_FILE}")
        return

    start_conversation(CONVERSATION_ID)

    print(f"\nConversation ID: {CONVERSATION_ID}")

    add_message(
        CONVERSATION_ID,
        "assistant",
        INTRO_TEXT.strip(),
    )

    listener = threading.Thread(
        target=keyboard_listener,
        daemon=True,
    )

    listener.start()

    print("\nStarting AI conversation...")

    no_response_count = 0

    try:

        # Play chairman introduction.
        playback_status = play_audio_with_interrupt(INTRO_FILE)

        while not quit_requested.is_set():

            if playback_status == "quit":
                break

            # Automatically listen after AI playback.
            recording_success = record_from_microphone()

            if not recording_success:

                if quit_requested.is_set():
                    break

                no_response_count += 1

                print(
                    f"\nNo response detected "
                    f"({no_response_count}/{MAX_NO_RESPONSE})"
                )

                if no_response_count >= MAX_NO_RESPONSE:

                    playback_status = play_fallback_message(
                        "Please vote for me. Thank you."
                    )

                    break

                playback_status = play_fallback_message(
                    "Are you there?"
                )

                continue

            # Speech-to-text.
            print("\nRecognising your speech...")

            try:

                question = transcribe_audio(INPUT_FILE)

                if not question or not question.strip():
                    raise ValueError("No speech recognised.")

                question = question.strip()

                no_response_count = 0

            except Exception as exc:

                no_response_count += 1

                print(
                    f"\nSTT failed "
                    f"({no_response_count}/{MAX_NO_RESPONSE}): {exc}"
                )

                if no_response_count >= MAX_NO_RESPONSE:

                    playback_status = play_fallback_message(
                        "Please vote for me. Thank you."
                    )

                    break

                playback_status = play_fallback_message(
                    "Are you there?"
                )

                continue

            print(f"\nCaller: {question}")

            if question.lower() in {
                "goodbye",
                "exit",
                "end conversation",
                "stop the call",
            }:
                print("Ending conversation.")
                break

            # Get conversation history.
            previous_messages = get_history(CONVERSATION_ID)

            conversation_context = [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in previous_messages
            ]

            # Generate LLM response.
            answer = generate_answer(
                question,
                conversation_history=conversation_context,
            )

            print(f"\nAssistant: {answer}")

            # Save conversation.
            add_message(CONVERSATION_ID, "user", question)
            add_message(CONVERSATION_ID, "assistant", answer)

            # Generate cloned voice.
            print("\nGenerating chairman's voice...")

            audio_file = generate_speech(
                answer,
                output_path=OUTPUT_FILE,
            )

            # Play response.
            playback_status = play_audio_with_interrupt(audio_file)

        print("\nConversation ended.")

    except KeyboardInterrupt:
        print("\nConversation stopped.")

    except Exception as exc:
        print(f"\nPipeline error: {exc}")

    finally:
        analyse_completed_call()


if __name__ == "__main__":
    main()
