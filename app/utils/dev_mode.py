"""Developer mode detection utility.

Reads CHATCOMPANION_DEV_MODE environment variable to determine if developer
mode is enabled. Developer mode enables additional debug information in the UI.
"""

import os


def is_dev_mode() -> bool:
    """
    Check if developer mode is enabled via environment variable.
    
    Developer mode is enabled if CHATCOMPANION_DEV_MODE is set to one of:
    - "1", "true", "yes", "on" (case-insensitive)
    
    Returns:
        True if developer mode is enabled, False otherwise (default)
    """
    env_value = os.getenv("CHATCOMPANION_DEV_MODE", "").strip().lower()
    return env_value in {"1", "true", "yes", "on"}

