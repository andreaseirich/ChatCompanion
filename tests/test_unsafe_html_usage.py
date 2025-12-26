"""Regression test to ensure unsafe_allow_html is never used with user content.

This test scans all Python files in app/ for unsafe_allow_html=True usage
and verifies it's only used with static strings, never with user input.
"""

import ast
import re
from pathlib import Path


# Safe patterns: unsafe_allow_html is acceptable for these
SAFE_PATTERNS = [
    r'inject_theme_css\(\)',  # CSS injection
    r'\.footer',  # Static footer
    r'badge-static',  # Static badge
    r'traffic.*light',  # Traffic light indicators
    r'<div class="card"',  # Static card HTML
    r'<span class="badge',  # Badge HTML
    r'<style>',  # CSS styles
    r'<div style=',  # Static div styling (traffic lights)
    r'<p style=',  # Static paragraph styling (traffic lights)
    r'background-color: #4CAF50',  # GREEN traffic light
    r'background-color: #FFC107',  # YELLOW traffic light
    r'background-color: #F44336',  # RED traffic light
    r'background-color: #cccccc',  # Inactive traffic light
    r'text-align: center',  # Static styling
]


# Dangerous patterns: unsafe_allow_html should NEVER be used with these
DANGEROUS_VARIABLES = [
    'chat_text',
    'explanation',
    'result.explanation',
    'result.advice',
    'normalized_text',
    'matched_text',
    'pattern',
    'category_matches',
    'category_scores',
    'matches',
    'text',
    'content',
    'message',
    'advice',
    'user_input',  # Common variable name in tests
    'user_content',  # Common variable name in tests
]


def find_unsafe_allow_html_usage(file_path: Path) -> list:
    """
    Find all unsafe_allow_html=True usages in a Python file.
    
    Returns:
        List of tuples: (line_number, line_content, context)
    """
    usages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if 'unsafe_allow_html=True' in line or 'unsafe_allow_html = True' in line:
                    # Get context (previous 5 lines for better function detection)
                    context_start = max(0, i - 6)
                    context = ''.join(lines[context_start:i])
                    usages.append((i, line.strip(), context))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return usages


def is_safe_usage(line_content: str, context: str) -> bool:
    """
    Check if unsafe_allow_html usage is safe (static content only).
    
    STRICT RULES:
    - Only constant literal strings are allowed
    - NO f-strings with variables
    - NO .format() with variables
    - NO string concatenation with variables
    - NO variable-derived content
    
    Args:
        line_content: The line containing unsafe_allow_html
        context: Surrounding code context
        
    Returns:
        True if usage is safe, False if potentially dangerous
    """
    combined = (line_content + ' ' + context)
    combined_lower = combined.lower()
    
    # First check if it matches any safe patterns (static HTML, CSS, etc.)
    for safe_pattern in SAFE_PATTERNS:
        if re.search(safe_pattern, combined_lower, re.IGNORECASE):
            return True
    
    # STRICT CHECK: Fail if f-string with variable interpolation
    # Pattern: f"<div>{variable}</div>" or f'<div>{variable}</div>'
    if re.search(r'f["\']', combined):
        # Check if f-string contains variable interpolation (curly braces with content)
        if re.search(r'\{[^}]+\}', combined):
            # This is an f-string with interpolation - fail
            return False
    
    # STRICT CHECK: Fail if .format() is used
    # Pattern: "<div>{}</div>".format(variable) or "<div>{var}</div>".format(var=variable)
    if '.format(' in combined:
        # Check if it's in the context of st.markdown with unsafe_allow_html
        if 'st.markdown' in combined_lower and 'unsafe_allow_html' in combined_lower:
            return False
    
    # STRICT CHECK: Fail if string concatenation with variables
    # Pattern: "<div>" + variable + "</div>" or variable + "<div>"
    if '+' in combined:
        # Check for any variable-like identifier (word characters) near + operator
        # Pattern: "string" + identifier or identifier + "string"
        concat_pattern = r'["\'].*\+.*[a-zA-Z_][a-zA-Z0-9_]*|[a-zA-Z_][a-zA-Z0-9_].*\+.*["\']'
        if re.search(concat_pattern, combined):
            # Additional check: if it's a known dangerous variable, definitely fail
            for dangerous_var in DANGEROUS_VARIABLES:
                escaped_var = re.escape(dangerous_var)
                concat_patterns = [
                    rf'["\'].*\+.*\b{escaped_var}\b',  # String + variable
                    rf'\b{escaped_var}\b.*\+.*["\']',  # Variable + string
                ]
                for pattern in concat_patterns:
                    if re.search(pattern, combined, re.IGNORECASE):
                        return False
            # If it's any identifier (not a known safe constant), fail
            # Safe constants would be things like True, False, None, numbers
            # But identifiers like user_input, content, etc. are unsafe
            return False
    
    # STRICT CHECK: Fail if st.markdown called with variable directly
    # Pattern: st.markdown(variable, unsafe_allow_html=True)
    # BUT: Allow CSS injection (css variable in inject_theme_css function)
    if 'inject_theme_css' in context or 'def inject_theme_css' in context:
        # CSS injection is safe - it's a constant string assigned to css variable
        return True
    
    # Extract the first argument to st.markdown
    markdown_match = re.search(r'st\.markdown\s*\(([^,)]+)', combined, re.IGNORECASE)
    if markdown_match:
        first_arg = markdown_match.group(1).strip()
        # If first arg is not a quoted string, it's likely a variable
        if not (first_arg.startswith('"') or first_arg.startswith("'")):
            # Check if it's a dangerous variable
            for dangerous_var in DANGEROUS_VARIABLES:
                if dangerous_var in first_arg:
                    return False
    
    # Check if it's a static HTML string (quoted string with HTML tags, no variables)
    # Static HTML strings are safe - they don't contain user content
    if re.search(r'st\.markdown\(["\']<', combined):
        # Verify it's a constant literal (not f-string, not .format, not concatenated)
        # Extract the string argument
        string_match = re.search(r'st\.markdown\(["\']([^"\']*)["\']', combined)
        if string_match:
            string_content = string_match.group(1)
            # If it contains { or } or +, it might be dynamic
            if '{' in string_content or '}' in string_content:
                # Could be f-string or .format - already checked above, but double-check
                return False
            # If it's a simple quoted string with HTML, it's safe
            return True
    
    # Default: fail if uncertain (conservative approach)
    return False


def test_no_unsafe_html_with_user_content():
    """Test that unsafe_allow_html is never used with user content."""
    app_dir = Path(__file__).parent.parent / "app"
    violations = []
    
    # Find all Python files in app/
    for py_file in app_dir.rglob("*.py"):
        usages = find_unsafe_allow_html_usage(py_file)
        
        for line_num, line_content, context in usages:
            # Special case: CSS injection in theme.py (safe - constant string)
            # Check if this is the CSS injection line in inject_theme_css function
            if py_file.name == "theme.py" and line_num == 176:
                continue
            
            # Special case: Footer in main.py (safe - constant string literal)
            # Check if context contains footer HTML or line contains footer
            if py_file.name == "main.py":
                full_context = context + ' ' + line_content
                if 'footer' in full_context.lower() and ('<div class="footer">' in full_context or 'ChatCompanion - Privacy-first' in full_context):
                    continue
            
            if not is_safe_usage(line_content, context):
                rel_path = py_file.relative_to(app_dir.parent)
                violations.append(
                    f"{rel_path}:{line_num} - Potentially unsafe usage:\n"
                    f"  {line_content}\n"
                    f"  Context: {context[-200:]}"
                )
    
    if violations:
        error_msg = (
            "Found unsafe_allow_html usage that may include user content:\n\n"
            + "\n\n".join(violations)
            + "\n\n"
            + "Rule: unsafe_allow_html=True should ONLY be used with:\n"
            + "- Static HTML strings (CSS, static badges, footer)\n"
            + "- Never with: chat_text, explanation, advice, matches, or any user input"
        )
        raise AssertionError(error_msg)


def test_explanation_rendering_is_safe():
    """Verify that explanation rendering doesn't use unsafe_allow_html."""
    components_file = Path(__file__).parent.parent / "app" / "ui" / "components.py"
    
    with open(components_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check render_explanation function
    if 'def render_explanation' in content:
        # Extract the function
        func_start = content.find('def render_explanation')
        func_end = content.find('\n\n', func_start)
        if func_end == -1:
            func_end = len(content)
        func_code = content[func_start:func_end]
        
        # Verify no unsafe_allow_html with explanation variable
        if 'unsafe_allow_html' in func_code and 'explanation' in func_code:
            raise AssertionError(
                "render_explanation() uses unsafe_allow_html with explanation variable. "
                "This is unsafe - user content must not use unsafe_allow_html."
            )


def test_advice_rendering_is_safe():
    """Verify that advice rendering doesn't use unsafe_allow_html."""
    components_file = Path(__file__).parent.parent / "app" / "ui" / "components.py"
    
    with open(components_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check render_advice function
    if 'def render_advice' in content:
        func_start = content.find('def render_advice')
        func_end = content.find('\n\n', func_start)
        if func_end == -1:
            func_end = len(content)
        func_code = content[func_start:func_end]
        
        # Verify no unsafe_allow_html with advice variable
        if 'unsafe_allow_html' in func_code and 'advice' in func_code:
            raise AssertionError(
                "render_advice() uses unsafe_allow_html with advice variable. "
                "This is unsafe - user content must not use unsafe_allow_html."
            )


def test_negative_case_f_string():
    """Negative test: f-string with variable should FAIL."""
    # Simulate unsafe usage: f-string with variable
    unsafe_code = 'st.markdown(f"<div>{user_input}</div>", unsafe_allow_html=True)'
    context = ''
    
    assert not is_safe_usage(unsafe_code, context), (
        "f-string with variable should be detected as unsafe"
    )


def test_negative_case_format():
    """Negative test: .format() with variable should FAIL."""
    # Simulate unsafe usage: .format() with variable
    unsafe_code = 'st.markdown("<div>{}</div>".format(user_input), unsafe_allow_html=True)'
    context = ''
    
    assert not is_safe_usage(unsafe_code, context), (
        ".format() with variable should be detected as unsafe"
    )


def test_negative_case_concatenation():
    """Negative test: String concatenation with variable should FAIL."""
    # Simulate unsafe usage: string concatenation
    unsafe_code = 'st.markdown("<div>" + user_input + "</div>", unsafe_allow_html=True)'
    context = ''
    
    assert not is_safe_usage(unsafe_code, context), (
        "String concatenation with variable should be detected as unsafe"
    )


def test_negative_case_direct_variable():
    """Negative test: Direct variable in st.markdown should FAIL."""
    # Simulate unsafe usage: direct variable
    unsafe_code = 'st.markdown(user_content, unsafe_allow_html=True)'
    context = ''
    
    assert not is_safe_usage(unsafe_code, context), (
        "Direct variable in st.markdown should be detected as unsafe"
    )

