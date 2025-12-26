"""Tests for Next Steps expander toggling logic."""

import pytest
from unittest.mock import MagicMock

from app.ui.components import render_next_steps
from app.utils.constants import RiskLevel


class TestNextStepsToggling:
    """Test that Next Steps expanders are mutually exclusive."""
    
    def test_show_no_click_sets_correct_state(self):
        """Test that clicking 'Show how to say NO' sets show_no_examples=True and show_professional_help=False."""
        # Test the callback logic directly by inspecting the function source
        import inspect
        
        source = inspect.getsource(render_next_steps)
        
        # Extract the on_show_no_click callback logic
        # Verify it sets show_no_examples=True and show_professional_help=False
        assert 'def on_show_no_click():' in source, "on_show_no_click callback should exist"
        assert 'show_no_examples = True' in source, "on_show_no_click should set show_no_examples=True"
        assert 'show_professional_help = False' in source, "on_show_no_click should set show_professional_help=False"
        
        # Verify the callback is used in button
        assert 'on_click=on_show_no_click' in source, "Button should use on_show_no_click callback"
    
    def test_get_help_click_sets_correct_state(self):
        """Test that clicking 'Get Professional Help' sets show_professional_help=True and show_no_examples=False."""
        # Test the callback logic directly by inspecting the function source
        import inspect
        
        source = inspect.getsource(render_next_steps)
        
        # Extract the on_get_help_click callback logic
        # Verify it sets show_professional_help=True and show_no_examples=False
        assert 'def on_get_help_click():' in source, "on_get_help_click callback should exist"
        assert 'show_professional_help = True' in source, "on_get_help_click should set show_professional_help=True"
        assert 'show_no_examples = False' in source, "on_get_help_click should set show_no_examples=False"
        
        # Verify the callback is used in button
        assert 'on_click=on_get_help_click' in source, "Button should use on_get_help_click callback"
    
    def test_green_shows_only_show_no_button(self):
        """Test that GREEN risk level shows only 'Show how to say NO' button prominently."""
        # This is a structural test - we verify the code structure
        import inspect
        
        source = inspect.getsource(render_next_steps)
        
        # Verify GREEN has single button logic
        assert 'if risk_level == RiskLevel.GREEN:' in source, "GREEN should have conditional logic"
        assert 'st.button("Show how to say NO"' in source, "GREEN should show 'Show how to say NO' button"
        assert 'Optional resources' in source, "GREEN should have 'Optional resources' expander"
        
        # Verify GREEN does NOT show "Get Professional Help" button prominently
        # (it should be in the else branch, not in the GREEN branch)
        green_section = source.split('if risk_level == RiskLevel.GREEN:')[1].split('else:')[0]
        assert 'Get Professional Help' not in green_section, "GREEN should NOT show 'Get Professional Help' button prominently"
    
    def test_yellow_red_show_both_buttons(self):
        """Test that YELLOW and RED risk levels show both buttons prominently."""
        import inspect
        
        source = inspect.getsource(render_next_steps)
        
        # Verify else branch (YELLOW/RED) has both buttons
        else_section = source.split('else:')[1] if 'else:' in source else ""
        
        assert 'st.button("Show how to say NO"' in else_section, "YELLOW/RED should show 'Show how to say NO' button"
        assert 'st.button("Get Professional Help"' in else_section, "YELLOW/RED should show 'Get Professional Help' button"
        assert 'st.columns(2)' in else_section, "YELLOW/RED should use columns for both buttons"
    
    def test_expanders_mutually_exclusive_logic(self):
        """Test that expanders are mutually exclusive via session state logic."""
        import inspect
        
        source = inspect.getsource(render_next_steps)
        
        # Verify callbacks set one to True and other to False
        assert 'show_no_examples = True' in source, "on_show_no_click should set show_no_examples=True"
        assert 'show_professional_help = False' in source, "on_show_no_click should set show_professional_help=False"
        assert 'show_professional_help = True' in source, "on_get_help_click should set show_professional_help=True"
        assert 'show_no_examples = False' in source, "on_get_help_click should set show_no_examples=False"
        
        # Verify expanders are conditionally rendered (only if state is True)
        assert 'if st.session_state.show_no_examples:' in source, "NO expander should only render if state is True"
        assert 'if st.session_state.show_professional_help:' in source, "Help expander should only render if state is True"

