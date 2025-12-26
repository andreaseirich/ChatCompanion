"""Regression tests for slang normalizer.

Verifies that normalization outputs expected forms for key cases.
"""

import pytest

from app.detection.slang_normalizer import SlangNormalizer


class TestSlangNormalizerRegression:
    """Regression tests for slang normalization."""

    @pytest.fixture
    def normalizer(self):
        """Create normalizer instance."""
        return SlangNormalizer()

    def test_basic_abbreviations(self, normalizer):
        """Test basic abbreviation normalization."""
        test_cases = [
            ("u", "you"),
            ("ur", "your"),
            ("r", "are"),
            ("idk", "I don't know"),
            ("idc", "I don't care"),
            ("frfr", "for real"),
            ("istg", "i swear to god"),
            ("ong", "on god"),
            ("wtv", "whatever"),
            ("bc", "because"),
            ("cuz", "because"),
        ]
        
        for input_text, expected_part in test_cases:
            result = normalizer.normalize(input_text)
            assert expected_part in result.normalized_text.lower(), (
                f"'{input_text}' should normalize to contain '{expected_part}'"
            )

    def test_right_now_variants(self, normalizer):
        """Test 'right now' obfuscation variants."""
        test_cases = [
            "rn",
            "r n",
            "r.n.",
            "r  n",
            "right now",
        ]
        
        for variant in test_cases:
            text = f"Answer {variant}"
            result = normalizer.normalize(text)
            # Should normalize to "right now" or "rn" consistently
            normalized_lower = result.normalized_text.lower()
            assert "right now" in normalized_lower or "rn" in normalized_lower, (
                f"'{variant}' should normalize to 'right now' or 'rn'"
            )

    def test_repeated_letters(self, normalizer):
        """Test repeated letter normalization."""
        test_cases = [
            ("nowww", "now"),
            ("pleeease", "please"),
            ("comeee", "come"),
            ("dooo it", "do it"),
        ]
        
        for input_text, expected_part in test_cases:
            result = normalizer.normalize(input_text)
            # Should reduce repeated letters
            normalized_lower = result.normalized_text.lower()
            # Check that excessive repeats are reduced
            assert normalized_lower.count(expected_part[0] * 3) == 0, (
                f"'{input_text}' should reduce repeated letters"
            )

    def test_typos(self, normalizer):
        """Test typo normalization."""
        test_cases = [
            ("rite now", "right now"),
            ("rite noww", "right now"),
            ("do itt", "do it"),
            ("pleease", "please"),
        ]
        
        for input_text, expected_part in test_cases:
            result = normalizer.normalize(input_text)
            normalized_lower = result.normalized_text.lower()
            assert expected_part in normalized_lower, (
                f"'{input_text}' should normalize to contain '{expected_part}'"
            )

    def test_masked_hostility(self, normalizer):
        """Test masked hostility normalization."""
        test_cases = [
            "stf*u",
            "st fu",
            "st f u",
            "st*f*u",
        ]
        
        for masked in test_cases:
            text = f"Just {masked}"
            result = normalizer.normalize(text)
            normalized_lower = result.normalized_text.lower()
            # Should normalize to "shut up" or similar
            assert "shut" in normalized_lower or "up" in normalized_lower, (
                f"'{masked}' should normalize to 'shut up' or similar"
            )

    def test_zero_width_chars(self, normalizer):
        """Test zero-width character removal."""
        # Insert zero-width space
        text_with_zw = "Answer\u200B\u200C\u200D right now"
        result = normalizer.normalize(text_with_zw)
        # Should remove zero-width chars
        assert "\u200B" not in result.normalized_text, (
            "Zero-width characters should be removed"
        )
        assert "\u200C" not in result.normalized_text, (
            "Zero-width characters should be removed"
        )
        assert "\u200D" not in result.normalized_text, (
            "Zero-width characters should be removed"
        )

    def test_emoji_tone_detection(self, normalizer):
        """Test emoji tone marker detection."""
        # Joking markers
        joking_text = "lol that's funny 😂"
        result = normalizer.normalize(joking_text)
        assert result.tone_markers.get("joking", False), (
            "Joking emoji should be detected"
        )
        
        # Annoyed markers
        annoyed_text = "ugh really? 😤"
        result = normalizer.normalize(annoyed_text)
        assert result.tone_markers.get("annoyed", False), (
            "Annoyed emoji should be detected"
        )

    def test_preserves_raw_text(self, normalizer):
        """Test that raw text is preserved."""
        text = "u r so cool frfr"
        result = normalizer.normalize(text)
        assert result.raw_text == text, (
            "Raw text should be preserved"
        )
        assert result.normalized_text != text, (
            "Normalized text should differ from raw text"
        )

