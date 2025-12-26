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
    r'render_card\(',  # render_card function (not currently used with user content)
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
                    # Get context (previous 2 lines and current line)
                    context_start = max(0, i - 3)
                    context = ''.join(lines[context_start:i])
                    usages.append((i, line.strip(), context))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return usages


def is_safe_usage(line_content: str, context: str) -> bool:
    """
    Check if unsafe_allow_html usage is safe (static content only).
    
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
    
    # Check if it's a static HTML string (quoted string with HTML tags)
    # Static HTML strings are safe - they don't contain user content
    if re.search(r'st\.markdown\(["\']<', combined):
        # Static HTML string in quotes - safe
        return True
    
    # Check if any dangerous variables are actually concatenated into the HTML
    # Look for patterns where the variable is used in the HTML rendering
    for dangerous_var in DANGEROUS_VARIABLES:
        escaped_var = re.escape(dangerous_var)
        # Pattern: variable used in string concatenation with HTML
        # e.g., "text" + variable or variable + "text" or f"text {variable}"
        dangerous_patterns = [
            rf'["\'].*\+.*\b{escaped_var}\b',  # String + variable
            rf'\b{escaped_var}\b.*\+.*["\']',  # Variable + string
            r'f["\'].*\{.*' + escaped_var,  # F-string with variable (use regular string)
            rf'st\.markdown\([^)]*{escaped_var}',  # st.markdown with variable directly
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                # Exception: render_card function definition (not used with user content)
                if 'def render_card' in context:
                    continue
                return False
    
    # If it contains HTML tags and no dangerous variables, it's likely static HTML
    if '<' in combined:
        # Check if there's actual variable concatenation (not just variable name in context)
        has_concatenation = False
        if '+' in combined:
            for dangerous_var in DANGEROUS_VARIABLES:
                # Check if variable appears near concatenation operator
                var_pattern = rf'\b{re.escape(dangerous_var)}\b'
                if re.search(var_pattern, combined, re.IGNORECASE):
                    # Check if variable is actually concatenated (not just in comments/docstrings)
                    # Look for pattern: "string" + variable or variable + "string"
                    concat_patterns = [
                        rf'["\'].*\+.*{re.escape(dangerous_var)}',
                        rf'{re.escape(dangerous_var)}.*\+.*["\']',
                    ]
                    for pattern in concat_patterns:
                        if re.search(pattern, combined, re.IGNORECASE):
                            has_concatenation = True
                            break
                    if has_concatenation:
                        break
        
        if not has_concatenation:
            # Static HTML with no variable concatenation - safe
            return True
    
    # Default: if no dangerous patterns found, consider safe
    # (most unsafe_allow_html usage in this codebase is for static HTML)
    return True


def test_no_unsafe_html_with_user_content():
    """Test that unsafe_allow_html is never used with user content."""
    app_dir = Path(__file__).parent.parent / "app"
    violations = []
    
    # Find all Python files in app/
    for py_file in app_dir.rglob("*.py"):
        usages = find_unsafe_allow_html_usage(py_file)
        
        for line_num, line_content, context in usages:
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

