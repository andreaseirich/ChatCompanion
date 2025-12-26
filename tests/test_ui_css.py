"""Tests for UI CSS rules and styling."""

from app.ui.theme import inject_theme_css


def test_anchor_icons_css_present():
    """Test that CSS rules to hide anchor icons are present in theme CSS."""
    # Get the CSS by calling inject_theme_css and capturing the output
    # Since inject_theme_css uses st.markdown, we need to inspect the function source
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify CSS contains selectors to hide anchor icons
    assert 'a[aria-label="Link to this section"]' in source, "CSS should hide anchor icons with aria-label"
    assert 'a.header-anchor' in source, "CSS should hide .header-anchor elements"
    assert 'a.anchor-link' in source, "CSS should hide .anchor-link elements"
    assert '.stMarkdown a[href^="#"][aria-label]' in source, "CSS should hide anchor links in markdown"
    assert 'h1 a, h2 a, h3 a' in source or 'h1 a' in source, "CSS should hide anchor links in headings"
    assert 'display: none !important' in source, "CSS should use display: none to hide anchors"
    
    # Verify external links are preserved
    assert 'http://' in source or 'https://' in source, "CSS should preserve external links"
    assert 'display: inline !important' in source, "CSS should preserve external links with display: inline"


def test_primary_button_styling_present():
    """Test that primary button styling (neutral blue) is present in theme CSS."""
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify primary button styling exists
    assert 'button[kind="primary"]' in source or 'button[type="primary"]' in source, "CSS should style primary buttons"
    assert '#1a73e8' in source, "CSS should use brand blue color (#1a73e8) for primary buttons"
    assert 'background-color: #1a73e8' in source, "CSS should set primary button background to brand blue"


def test_spacing_css_present():
    """Test that compact spacing CSS rules are present."""
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify spacing rules for status dots
    assert '.status-dot-container' in source, "CSS should style status-dot-container"
    assert 'margin-top: 8px' in source or 'margin-top:8px' in source, "CSS should have compact margins"
    assert 'margin-bottom: 8px' in source or 'margin-bottom:8px' in source, "CSS should have compact margins"


def test_next_steps_panel_styling_present():
    """Test that Next Steps panel styling is present."""
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify panel styling exists
    assert '.element-container' in source or 'element-container' in source, "CSS should style element containers"
    assert '#f8f9fa' in source, "CSS should use light background for panels"
    assert 'border-radius: 12px' in source or 'border-radius:12px' in source, "CSS should have rounded corners for panels"

