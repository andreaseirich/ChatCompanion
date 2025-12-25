"""Text processing utilities for chat analysis."""

import re
from typing import List


def normalize_text(text: str) -> str:
    """
    Normalize chat text for analysis.

    Args:
        text: Raw chat text

    Returns:
        Normalized text
    """
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def segment_sentences(text: str) -> List[str]:
    """
    Segment text into sentences.

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    # Simple sentence segmentation
    # Split on sentence-ending punctuation
    sentences = re.split(r"[.!?]+", text)
    # Filter out empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def extract_message_pairs(text: str) -> List[tuple]:
    """
    Extract message pairs from chat text (if formatted as conversation).

    Args:
        text: Chat text (may contain speaker labels)

    Returns:
        List of (speaker, message) tuples, or [(None, text)] if no structure
    """
    # Simple pattern: "Speaker: message"
    pattern = r"(\w+):\s*(.+?)(?=\n\w+:|$)"
    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)

    if matches:
        return [(speaker.strip(), msg.strip()) for speaker, msg in matches]
    else:
        # No structure found, return as single message
        return [(None, text)]

