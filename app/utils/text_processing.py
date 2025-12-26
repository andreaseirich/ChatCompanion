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


def get_sentence_context(text: str, position: int, window: int = 1) -> str:
    """
    Get sentence context around a given position.

    Args:
        text: Full text
        position: Character position in text
        window: Number of adjacent sentences to include (default: 1)

    Returns:
        Context string containing the sentence with the position and adjacent sentences
    """
    sentences = segment_sentences(text)
    
    # Find which sentence contains the position
    current_pos = 0
    sentence_index = -1
    
    for i, sentence in enumerate(sentences):
        sentence_end = current_pos + len(sentence)
        if current_pos <= position < sentence_end:
            sentence_index = i
            break
        current_pos = sentence_end + 1  # +1 for sentence delimiter
    
    if sentence_index == -1:
        # Position not found in any sentence, return empty
        return ""
    
    # Get context window: sentence_index ± window
    start_idx = max(0, sentence_index - window)
    end_idx = min(len(sentences), sentence_index + window + 1)
    
    context_sentences = sentences[start_idx:end_idx]
    return " ".join(context_sentences)

