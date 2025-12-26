"""Test mode detection for ChatCompanion.

Allows bypassing certain UI delays and animations during automated testing.
"""

import os


def is_test_mode() -> bool:
    """
    Checks if the application is running in test mode.

    Test mode is enabled if the CHATCOMPANION_TEST_MODE environment variable
    is set to "1", "true", "yes", or "on" (case-insensitive).
    
    Returns:
        True if test mode is enabled, False otherwise
    """
    test_mode_env = os.environ.get("CHATCOMPANION_TEST_MODE", "").lower()
    return test_mode_env in {"1", "true", "yes", "on"}

