
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "conversation_history.json"

# Each conversation contains messages and call analysis.
history = {}


def load_history() -> None:
    """Load and migrate saved conversations from disk."""
    global history

    if not HISTORY_FILE.exists():
        return

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            loaded = json.load(file)

        if not isinstance(loaded, dict):
            return

        migrated = {}

        for conversation_id, data in loaded.items():

            # Existing format: conversation_id -> list of messages
            if isinstance(data, list):
                migrated[conversation_id] = {
                    "messages": data,
                    "call_analysis": None,
                }

            # New format: conversation_id -> object
            elif isinstance(data, dict):
                migrated[conversation_id] = {
                    "messages": data.get("messages", []),
                    "call_analysis": data.get("call_analysis"),
                }

        history = migrated

        # Save migrated format.
        save_history()

    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: Could not load conversation history: {exc}")


def save_history() -> None:
    """Persist conversations to a JSON file."""
    temporary_file = HISTORY_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)

    temporary_file.replace(HISTORY_FILE)


def start_conversation(conversation_id: str) -> None:
    """Create a conversation if it doesn't already exist."""
    if conversation_id not in history:
        history[conversation_id] = {
            "messages": [],
            "call_analysis": None,
        }
        save_history()


def get_history(conversation_id: str) -> list[dict]:
    """Return the messages for a conversation."""
    start_conversation(conversation_id)

    return history[conversation_id]["messages"]


def add_message(
    conversation_id: str,
    role: str,
    content: str,
) -> None:
    """Store one user or assistant message."""
    if role not in {"user", "assistant"}:
        raise ValueError("Role must be 'user' or 'assistant'.")

    start_conversation(conversation_id)

    history[conversation_id]["messages"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    save_history()


def save_call_analysis(
    conversation_id: str,
    analysis: dict,
) -> None:
    """Save the final AI-generated call analysis."""

    start_conversation(conversation_id)

    history[conversation_id]["call_analysis"] = {
        "summary": str(analysis["summary"]),
        "interest_score": max(
            0,
            min(100, int(analysis["interest_score"])),
        ),
        "need_human": bool(analysis["need_human"]),
        "call_again": bool(analysis["call_again"]),
    }

    save_history()


load_history()
