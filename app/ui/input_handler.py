"""Chat input handling for UI."""

from pathlib import Path
from typing import Optional


def load_demo_chats(demo_dir: Path) -> dict:
    """
    Load demo chat files.

    Args:
        demo_dir: Directory containing demo chat files

    Returns:
        Dictionary mapping chat names to content
    """
    demo_chats = {}
    chats_dir = demo_dir / "chats"

    if not chats_dir.exists():
        return demo_chats

    # Expected demo chat files
    demo_files = {
        "safe_chat.txt": "Safe Chat Example",
        "bullying_example.txt": "Bullying Example",
        "manipulation_example.txt": "Manipulation Example",
        "grooming_example.txt": "Grooming Example",
    }

    for filename, display_name in demo_files.items():
        filepath = chats_dir / filename
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    demo_chats[display_name] = content
            except Exception:
                continue

    return demo_chats


def get_chat_input(demo_chats: dict) -> Optional[str]:
    """
    Get chat input from user (either manual input or demo selection).

    Args:
        demo_chats: Dictionary of available demo chats

    Returns:
        Chat text or None if no input provided
    """
    # This function will be called from the main Streamlit app
    # It's a placeholder for the input logic
    return None

