"""Unit tests for developer mode detection."""

import os
import pytest

from app.utils.dev_mode import is_dev_mode


class TestDevMode:
    """Test developer mode detection."""

    def test_dev_mode_enabled_with_1(self, monkeypatch):
        """Test that dev mode is enabled when CHATCOMPANION_DEV_MODE=1."""
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "1")
        assert is_dev_mode() is True

    def test_dev_mode_enabled_with_true(self, monkeypatch):
        """Test that dev mode is enabled when CHATCOMPANION_DEV_MODE=true."""
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "true")
        assert is_dev_mode() is True

    def test_dev_mode_enabled_with_yes(self, monkeypatch):
        """Test that dev mode is enabled when CHATCOMPANION_DEV_MODE=yes."""
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "yes")
        assert is_dev_mode() is True

    def test_dev_mode_enabled_with_on(self, monkeypatch):
        """Test that dev mode is enabled when CHATCOMPANION_DEV_MODE=on."""
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "on")
        assert is_dev_mode() is True

    def test_dev_mode_case_insensitive(self, monkeypatch):
        """Test that dev mode detection is case-insensitive."""
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "TRUE")
        assert is_dev_mode() is True
        
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "Yes")
        assert is_dev_mode() is True
        
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "ON")
        assert is_dev_mode() is True

    def test_dev_mode_disabled_by_default(self, monkeypatch):
        """Test that dev mode is disabled when env var is not set."""
        monkeypatch.delenv("CHATCOMPANION_DEV_MODE", raising=False)
        assert is_dev_mode() is False

    def test_dev_mode_disabled_with_other_values(self, monkeypatch):
        """Test that dev mode is disabled with other values."""
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "0")
        assert is_dev_mode() is False
        
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "false")
        assert is_dev_mode() is False
        
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "no")
        assert is_dev_mode() is False
        
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", "off")
        assert is_dev_mode() is False

    def test_dev_mode_handles_whitespace(self, monkeypatch):
        """Test that dev mode handles whitespace in env var value."""
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", " 1 ")
        assert is_dev_mode() is True
        
        monkeypatch.setenv("CHATCOMPANION_DEV_MODE", " true ")
        assert is_dev_mode() is True

