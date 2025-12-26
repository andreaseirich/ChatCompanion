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
    # Check if any dangerous variables appear in the context
    combined = (line_content + ' ' + context).lower()
    
    for dangerous_var in DANGEROUS_VARIABLES:
        # Look for variable usage patterns
        # Escape the variable name for regex
        escaped_var = re.escape(dangerous_var)
        patterns = [
            rf'\b{escaped_var}\b',  # Variable name
            rf'\+.*{escaped_var}',  # String concatenation
            rf'{escaped_var}\s*\+',  # Variable concatenation
            rf'f["\'].*\{.*{escaped_var}',  # F-string
        ]
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                return False
    
    # Check if it matches any safe patterns
    for safe_pattern in SAFE_PATTERNS:
        if re.search(safe_pattern, combined, re.IGNORECASE):
            return True
    
    # If it's a simple static string (quoted), it's likely safe
    # But we'll be conservative and flag it for manual review
    if '"' in line_content or "'" in line_content:
        # Check if it's a simple string literal (not concatenated with variables)
        if '+' not in context or all(
            part.strip().startswith(('"', "'")) 
            for part in context.split('+') 
            if part.strip()
        ):
            return True
    
    # Default: flag as potentially unsafe for manual review
    return False


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

