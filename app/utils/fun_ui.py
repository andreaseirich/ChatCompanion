"""Fun UI features detection utility.

Reads CHATCOMPANION_FUN_UI environment variable to determine if fun UI features
(such as balloons) should be enabled. Defaults to enabled if not set.
"""

import os


def is_fun_ui_enabled() -> bool:
    """
    Check if fun UI features are enabled via environment variable.
    
    Fun UI is enabled by default. It can be disabled by setting
    CHATCOMPANION_FUN_UI to "0", "false", "no", or "off" (case-insensitive).
    
    Returns:
        True if fun UI is enabled (default), False if explicitly disabled
    """
    env_value = os.getenv("CHATCOMPANION_FUN_UI", "").strip().lower()
    
    # Default to enabled if not set or set to enabled values
    if not env_value or env_value in {"1", "true", "yes", "on"}:
        return True
    
    # Disabled if explicitly set to disabled values
    if env_value in {"0", "false", "no", "off"}:
        return False
    
    # Default to enabled for any other value
    return True

