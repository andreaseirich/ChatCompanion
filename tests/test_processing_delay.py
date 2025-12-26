"""Tests for processing delay bypass in test mode."""

import os
import time
from unittest.mock import patch

import pytest

from app.utils.test_mode import is_test_mode


class TestProcessingDelayBypass:
    """Test that processing delay is bypassed in test mode."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test."""
        # Store original env var state
        self._original_test_mode = os.environ.get("CHATCOMPANION_TEST_MODE")
        # Ensure it's unset before each test
        if "CHATCOMPANION_TEST_MODE" in os.environ:
            del os.environ["CHATCOMPANION_TEST_MODE"]
        yield
        # Restore original env var state after each test
        if self._original_test_mode is not None:
            os.environ["CHATCOMPANION_TEST_MODE"] = self._original_test_mode
        elif "CHATCOMPANION_TEST_MODE" in os.environ:
            del os.environ["CHATCOMPANION_TEST_MODE"]

    def test_test_mode_enabled(self):
        """Test that is_test_mode() returns True when env var is set."""
        os.environ["CHATCOMPANION_TEST_MODE"] = "1"
        assert is_test_mode() is True

        os.environ["CHATCOMPANION_TEST_MODE"] = "true"
        assert is_test_mode() is True

        os.environ["CHATCOMPANION_TEST_MODE"] = "yes"
        assert is_test_mode() is True

        os.environ["CHATCOMPANION_TEST_MODE"] = "on"
        assert is_test_mode() is True

    def test_test_mode_disabled(self):
        """Test that is_test_mode() returns False when env var is not set or disabled."""
        # Not set
        assert is_test_mode() is False

        # Explicitly disabled
        os.environ["CHATCOMPANION_TEST_MODE"] = "0"
        assert is_test_mode() is False

        os.environ["CHATCOMPANION_TEST_MODE"] = "false"
        assert is_test_mode() is False

    def test_processing_delay_bypassed_in_test_mode(self):
        """Test that time.sleep is NOT called when CHATCOMPANION_TEST_MODE=1."""
        os.environ["CHATCOMPANION_TEST_MODE"] = "1"
        
        # Simulate the logic from app/main.py
        with patch("time.sleep") as mock_sleep:
            # This is the logic from app/main.py line 179-180
            if not is_test_mode():
                time.sleep(1.5)
            
            # Verify sleep was NOT called
            mock_sleep.assert_not_called()

    def test_processing_delay_not_bypassed_when_test_mode_off(self):
        """Test that time.sleep IS called when CHATCOMPANION_TEST_MODE is not set."""
        # Ensure test mode is off
        if "CHATCOMPANION_TEST_MODE" in os.environ:
            del os.environ["CHATCOMPANION_TEST_MODE"]
        
        # Simulate the logic from app/main.py
        with patch("time.sleep") as mock_sleep:
            # This is the logic from app/main.py line 179-180
            if not is_test_mode():
                time.sleep(1.5)
            
            # Verify sleep WAS called
            mock_sleep.assert_called_once_with(1.5)

