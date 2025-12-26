"""Slang and abbreviation normalizer for youth/online language."""

import re
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizedMessage:
    """Result of slang normalization."""

    raw_text: str
    normalized_text: str
    replacements: List[Dict[str, str]] = field(default_factory=list)
    has_emoji: bool = False
    tone_markers: Dict[str, bool] = field(default_factory=dict)


class SlangNormalizer:
    """Normalizes common English youth/online slang and abbreviations."""

    def __init__(self):
        """Initialize the slang normalizer with abbreviation mappings."""
        # Common abbreviations mapping (abbreviation -> normalized form)
        # Order matters: longer patterns first to avoid partial matches
        self.abbreviations = {
            # Pronouns and common words
            "ur": "your",
            "u": "you",
            "r": "are",
            "y": "why",
            "c": "see",
            "b": "be",
            "n": "and",
            # Common phrases
            "idk": "I don't know",
            "idc": "I don't care",
            "brb": "be right back",
            "btw": "by the way",
            "omg": "oh my god",
            "jk": "just kidding",
            "fr": "for real",
            "ngl": "not going to lie",
            "wyd": "what are you doing",
            "smh": "shaking my head",
            "tbh": "to be honest",
            "imo": "in my opinion",
            "fyi": "for your information",
            "np": "no problem",
            "ty": "thank you",
            "thx": "thank you",
            "yw": "you're welcome",
            "gg": "good game",
            "gl": "good luck",
            "hf": "have fun",
            "af": "as fuck",  # Preserve intensity
            "rn": "right now",
            "tmr": "tomorrow",
            "tmrw": "tomorrow",
            "ttyl": "talk to you later",
            "ily": "I love you",
            "ily2": "I love you too",
            "hbu": "how about you",
            "wbu": "what about you",
            "nvm": "never mind",
            "ikr": "I know right",
            "fml": "fuck my life",  # Preserve negativity
            "wtf": "what the fuck",  # Preserve intensity
            "omw": "on my way",
            "tmi": "too much information",
            # Hostile slang (preserve hostility)
            "stfu": "shut up",
            # Laughing expressions (normalize to consistent form)
            "lol": "laughing",
            "lmao": "laughing",
            "lmfao": "laughing",
            "rofl": "laughing",
            "haha": "haha",  # Keep as is
            "hehe": "hehe",  # Keep as is
        }

        # Sort by length (longest first) to avoid partial matches
        self.sorted_abbrevs = sorted(
            self.abbreviations.items(), key=lambda x: len(x[0]), reverse=True
        )

        # Emoji patterns for tone detection
        self.joking_emojis = ["😂", "🤣", "😅", "😆", "😊", "😄"]
        self.annoyed_emojis = ["😒", "😑", "🙄", "💢", "😤", "😠"]

    def normalize_message(self, text: str) -> NormalizedMessage:
        """
        Normalize slang and abbreviations in text.

        Args:
            text: Raw chat text

        Returns:
            NormalizedMessage with normalized text and metadata
        """
        raw_text = text
        normalized = text
        replacements = []
        has_emoji = False
        tone_markers = {"joking": False, "annoyed": False}

        # Detect emojis (light detection only)
        for emoji in self.joking_emojis:
            if emoji in text:
                has_emoji = True
                tone_markers["joking"] = True
                break

        for emoji in self.annoyed_emojis:
            if emoji in text:
                has_emoji = True
                tone_markers["annoyed"] = True
                break

        # Normalize abbreviations (case-insensitive, word boundaries)
        # Use word boundaries to avoid partial matches
        for abbrev, replacement in self.sorted_abbrevs:
            # Case-insensitive pattern with word boundaries
            pattern = r"\b" + re.escape(abbrev) + r"\b"
            matches = re.finditer(pattern, normalized, re.IGNORECASE)

            # Collect all matches first (to avoid position shifts)
            match_list = list(matches)

            # Replace from end to start to preserve positions
            for match in reversed(match_list):
                original = match.group(0)
                normalized = (
                    normalized[: match.start()] + replacement + normalized[match.end() :]
                )
                replacements.append({"original": original, "normalized": replacement})

        return NormalizedMessage(
            raw_text=raw_text,
            normalized_text=normalized,
            replacements=replacements,
            has_emoji=has_emoji,
            tone_markers=tone_markers,
        )

