"""Tests for UI CSS rules and styling."""

from app.ui.theme import inject_theme_css


def test_anchor_icons_css_present():
    """Test that CSS rules to hide anchor icons are present in theme CSS."""
    # Get the CSS by calling inject_theme_css and capturing the output
    # Since inject_theme_css uses st.markdown, we need to inspect the function source
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify CSS contains selectors to hide anchor icons (including fallback selectors)
    assert 'a[aria-label="Link to this section"]' in source, "CSS should hide anchor icons with aria-label"
    assert 'a.header-anchor' in source, "CSS should hide .header-anchor elements"
    assert 'a.anchor-link' in source, "CSS should hide .anchor-link elements"
    assert 'a[class*="anchor"]' in source, "CSS should hide anchor elements with class containing 'anchor' (fallback)"
    assert 'a[class*="header"]' in source, "CSS should hide anchor elements with class containing 'header' (fallback)"
    assert '.stMarkdown a[href^="#"][aria-label]' in source, "CSS should hide anchor links in markdown"
    assert '.stMarkdown h1 > a' in source or '.stMarkdown h2 > a' in source or '.stMarkdown h3 > a' in source, "CSS should hide anchor links in markdown headings"
    assert 'h1 a, h2 a, h3 a' in source or 'h1 a' in source, "CSS should hide anchor links in headings"
    assert 'display: none !important' in source, "CSS should use display: none to hide anchors"
    
    # Verify external links are preserved
    assert 'http://' in source or 'https://' in source, "CSS should preserve external links"
    assert 'display: inline !important' in source, "CSS should preserve external links with display: inline"


def test_primary_button_styling_present():
    """Test that primary button styling uses brand CSS variables."""
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify primary button styling exists and uses CSS variables
    assert 'button[kind="primary"]' in source or 'button[type="primary"]' in source, "CSS should style primary buttons"
    assert 'var(--brand-primary)' in source, "CSS should use --brand-primary variable for primary buttons"
    assert 'background-color: var(--brand-primary)' in source, "CSS should set primary button background using CSS variable"
    
    # Verify no hardcoded #1a73e8 in button styling (may appear in comments, which is fine)
    # Check that button styling section doesn't contain hardcoded color
    button_section_start = source.find('/* Primary button styling')
    if button_section_start != -1:
        button_section_end = source.find('/*', button_section_start + 1)
        if button_section_end == -1:
            button_section_end = len(source)
        button_section = source[button_section_start:button_section_end]
        # Allow #1a73e8 only in comments (after /* or //)
        if '#1a73e8' in button_section:
            # Check if it's in a comment
            comment_start = button_section.rfind('/*', 0, button_section.find('#1a73e8'))
            comment_end = button_section.find('*/', button_section.find('#1a73e8'))
            if comment_start == -1 or comment_end == -1 or comment_end < comment_start:
                # Not in a comment - this is a violation
                assert False, "Primary button styling should not use hardcoded #1a73e8, use CSS variables instead"


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


def test_brand_variables_defined():
    """Test that brand CSS variables are defined in :root."""
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify :root block exists with brand variables
    assert ':root' in source, "CSS should define :root for CSS variables"
    assert '--brand-primary' in source, "CSS should define --brand-primary variable"
    assert '--brand-primary-hover' in source, "CSS should define --brand-primary-hover variable"
    assert '--focus-ring' in source, "CSS should define --focus-ring variable"
    
    # Verify variables are set to values (not empty)
    assert '--brand-primary: #' in source, "CSS should set --brand-primary to a color value"
    assert '--brand-primary-hover: #' in source, "CSS should set --brand-primary-hover to a color value"
    assert '--focus-ring:' in source, "CSS should set --focus-ring to a value"


def test_focus_visible_states_present():
    """Test that :focus-visible CSS rules are present for accessibility."""
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify focus-visible rules exist
    assert ':focus-visible' in source, "CSS should include :focus-visible rules for accessibility"
    assert 'button:focus-visible' in source or '.stButton > button:focus-visible' in source, "CSS should style button focus states"
    assert 'textarea:focus-visible' in source or '.stTextArea' in source and ':focus-visible' in source, "CSS should style textarea focus states"
    assert 'expanderHeader:focus-visible' in source or '.streamlit-expanderHeader:focus-visible' in source, "CSS should style expander header focus states"
    
    # Verify focus ring uses CSS variable
    assert 'var(--focus-ring)' in source, "CSS should use --focus-ring variable for focus states"


def test_anchor_icon_hiding_robust():
    """Test that anchor icon hiding is robust with multiple selectors and doesn't break content links."""
    import inspect
    
    source = inspect.getsource(inject_theme_css)
    
    # Verify multiple anchor hiding selectors exist (robustness)
    assert 'a[aria-label="Link to this section"]' in source, "CSS should hide anchor icons with aria-label"
    assert 'a.header-anchor' in source, "CSS should hide .header-anchor elements"
    assert 'a.anchor-link' in source, "CSS should hide .anchor-link elements"
    assert 'a[class*="anchor"]' in source, "CSS should hide anchor elements with class containing 'anchor' (fallback)"
    assert 'a[class*="header"]' in source, "CSS should hide anchor elements with class containing 'header' (fallback)"
    assert '.stMarkdown h1 > a' in source or '.stMarkdown h2 > a' in source, "CSS should hide anchor links in markdown headings"
    
    # Verify content links are NOT hidden (preserved)
    assert '.stMarkdown a[href^="http://"]' in source or '.stMarkdown a[href^="https://"]' in source, "CSS should preserve external links"
    assert 'display: inline !important' in source, "CSS should explicitly preserve external links with display: inline"
    assert '.stMarkdown a:not([href^="#"])' in source, "CSS should preserve content links (not starting with #)"
    
    # Verify comment explaining intent exists
    assert 'Intent:' in source or 'intent:' in source or 'Hide anchor icons' in source, "CSS should include comment explaining anchor hiding intent"

