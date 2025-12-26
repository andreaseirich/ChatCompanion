"""Slang and abbreviation normalizer for youth/online language."""

import re
import unicodedata
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

    def _normalize_obfuscation(self, text: str) -> str:
        """
        Normalize obfuscated words (e.g., "stf*u" -> "stfu").

        Args:
            text: Input text

        Returns:
            Text with obfuscation removed
        """
        # Remove asterisks and other common obfuscation chars within words
        # Pattern: word char, obfuscation char(s), word char
        text = re.sub(r"(\w)[*_\-\.]+(\w)", r"\1\2", text)
        return text

    def _normalize_letter_repeats(self, text: str, max_repeats: int = 2) -> str:
        """
        Normalize excessive letter repeats (e.g., "righttt" -> "right").

        Args:
            text: Input text
            max_repeats: Maximum allowed consecutive repeats (default: 2)

        Returns:
            Text with letter repeats normalized
        """
        # Pattern: capture a letter, then find 3+ repeats of same letter
        # Replace with max_repeats copies
        def replace_repeats(match):
            char = match.group(1)
            return char * max_repeats

        # Match 3+ consecutive identical letters (case-insensitive)
        pattern = r"([a-zA-Z])\1{2,}"
        text = re.sub(pattern, replace_repeats, text, flags=re.IGNORECASE)
        return text

    def _normalize_spacing_variants(self, text: str) -> str:
        """
        Normalize spacing/punctuation variants (e.g., "r n" -> "rn", "r.n." -> "rn").

        Args:
            text: Input text

        Returns:
            Text with spacing variants normalized
        """
        # Common spacing variants for abbreviations
        # "r n" -> "rn", "r.n." -> "rn", "r-n" -> "rn"
        spacing_variants = [
            (r"\br\s+\.?\s*n\b", "rn"),  # "r n" or "r.n" -> "rn"
            (r"\br\s*\.\s*n\b", "rn"),   # "r.n" -> "rn"
            (r"\br\s*-\s*n\b", "rn"),    # "r-n" -> "rn"
        ]

        for pattern, replacement in spacing_variants:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _normalize_typos(self, text: str) -> str:
        """
        Normalize common typos (e.g., "rite now" -> "right now").

        Args:
            text: Input text

        Returns:
            Text with typos corrected
        """
        # Common typo corrections
        typo_map = {
            r"\brite\s+now\b": "right now",
            r"\brightt\s+now\b": "right now",
            r"\bnoww+\b": "now",
        }

        for pattern, replacement in typo_map.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _remove_zero_width_chars(self, text: str) -> str:
        """
        Remove zero-width characters and normalize Unicode.

        Args:
            text: Input text

        Returns:
            Text with zero-width chars removed
        """
        # Remove zero-width spaces, joiners, etc.
        text = "".join(char for char in text if unicodedata.category(char) != "Cf" or char in ["\n", "\r", "\t"])
        return text

    def normalize_message(self, text: str) -> NormalizedMessage:
        """
        Normalize slang and abbreviations in text.

        Args:
            text: Raw chat text

        Returns:
            NormalizedMessage with normalized text and metadata
        """
        raw_text = text
        
        # Step 1: Remove zero-width characters
        normalized = self._remove_zero_width_chars(text)
        
        # Step 2: Casefold (lowercase) for consistent matching
        normalized_lower = normalized.casefold()
        
        # Step 3: Normalize obfuscation (e.g., "stf*u" -> "stfu")
        normalized = self._normalize_obfuscation(normalized)
        
        # Step 4: Normalize spacing variants (e.g., "r n" -> "rn")
        normalized = self._normalize_spacing_variants(normalized)
        
        # Step 5: Normalize letter repeats (e.g., "righttt" -> "right")
        normalized = self._normalize_letter_repeats(normalized)
        
        # Step 6: Normalize typos (e.g., "rite now" -> "right now")
        normalized = self._normalize_typos(normalized)
        
        replacements = []
        has_emoji = False
        tone_markers = {"joking": False, "annoyed": False}

        # Detect emojis (light detection only)
        for emoji in self.joking_emojis:
            if emoji in normalized:
                has_emoji = True
                tone_markers["joking"] = True
                break

        for emoji in self.annoyed_emojis:
            if emoji in normalized:
                has_emoji = True
                tone_markers["annoyed"] = True
                break

        # Step 7: Normalize abbreviations (case-insensitive, word boundaries)
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

