#!/usr/bin/env python3
"""
Repository Hygiene Checker

Scans the repository for disallowed patterns that should not be committed.
Focuses on real leaks: sensitive file paths, secret patterns, and internal artifacts.

Usage:
    python scripts/repo_hygiene_check.py

Exit codes:
    0: No violations found
    1: Violations found
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# Disallowed file paths/patterns (case-insensitive, must match full path or filename)
DISALLOWED_PATHS = [
    r"\.env",
    r"\.env\.",
    r"\.pem$",
    r"id_rsa",
    r"id_dsa",
    r"\.local/",
    r"scratch",
    r"notes\.txt$",
    r"notes\.md$",
    r"debug_prompt",
    r"master_prompt",
]

# Disallowed filename patterns (only for suspicious filenames, not content)
DISALLOWED_FILENAMES = [
    r"^\.env",
    r"\.pem$",
    r"^id_rsa",
    r"^id_dsa",
    r"scratch",
    r"debug_prompt",
    r"master_prompt",
]

# Secret-like content patterns (regex) - only strong signatures
SECRET_PATTERNS = [
    (r"BEGIN\s+(RSA\s+)?PRIVATE\s+KEY", "Private key detected"),
    (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY", "Private key block detected"),
    (r"-----BEGIN\s+(CERTIFICATE|X509)", "Certificate detected"),
    (r"api[_-]?key\s*=\s*['\"]?[a-zA-Z0-9]{32,}", "API key pattern detected (32+ chars)"),
    (r"token\s*=\s*['\"]?[a-zA-Z0-9]{32,}", "Token pattern detected (32+ chars)"),
    (r"secret[_-]?key\s*=\s*['\"]?[a-zA-Z0-9]{32,}", "Secret key pattern detected"),
    (r"password\s*=\s*['\"]?[^'\"]{12,}", "Password pattern detected (12+ chars)"),
    (r"AWS_ACCESS_KEY_ID\s*=\s*['\"]?[A-Z0-9]{20,}", "AWS access key ID detected"),
    (r"AWS_SECRET_ACCESS_KEY\s*=\s*['\"]?[A-Za-z0-9/+=]{40,}", "AWS secret access key detected"),
    (r"GITHUB_TOKEN\s*=\s*['\"]?(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}", "GitHub token detected"),
    (r"SLACK_TOKEN\s*=\s*['\"]?xox[baprs]-[0-9a-zA-Z-]{10,}", "Slack token detected"),
    (r"connection[_-]?string\s*=\s*['\"].*password.*['\"]", "Connection string with password detected"),
    (r"mongodb[+srv]*://[^:]+:[^@]+@", "MongoDB connection string with credentials detected"),
    (r"postgresql://[^:]+:[^@]+@", "PostgreSQL connection string with credentials detected"),
    (r"mysql://[^:]+:[^@]+@", "MySQL connection string with credentials detected"),
]

# Allowed directories (excluded from scanning)
ALLOWED_DIRS = [
    ".git",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".streamlit",
    "dist",
    "build",
    "models",  # Model files are large and gitignored
]

# Allowlist: files that may contain false positives
ALLOWLIST = {
    # File path -> allowed patterns in filename or content
    "docs/ARCHITECTURE.md": ["prompt"],  # May discuss "prompt engineering"
    "docs/ETHICS.md": ["private"],  # May discuss "privacy"
    "docs/SECURITY.md": ["private", "secret"],  # Security documentation
    "CONTRIBUTING.md": ["private", "secret"],  # Contributing guidelines
    ".gitignore": ["local", "private"],  # Gitignore patterns
    "README.md": ["private"],  # Privacy discussion
    "scripts/repo_hygiene_check.py": ["postgresql", "mysql", "mongodb"],  # Contains regex patterns for detection
}

# Maximum file size to scan for content (1MB)
MAX_FILE_SIZE = 1024 * 1024


def is_allowed_path(file_path: Path) -> bool:
    """Check if a file path should be excluded from scanning."""
    # Check if path is in an allowed directory
    for allowed_dir in ALLOWED_DIRS:
        if allowed_dir in file_path.parts:
            return True
    return False


def check_path_patterns(file_path: Path) -> List[str]:
    """Check if file path matches disallowed patterns."""
    violations = []
    path_str = str(file_path).lower()
    
    for pattern in DISALLOWED_PATHS:
        if re.search(pattern, path_str, re.IGNORECASE):
            violations.append(f"Path matches disallowed pattern: '{pattern}'")
    
    return violations


def check_filename_patterns(filename: str) -> List[str]:
    """Check if filename matches disallowed patterns."""
    violations = []
    filename_lower = filename.lower()
    
    for pattern in DISALLOWED_FILENAMES:
        if re.search(pattern, filename_lower):
            violations.append(f"Filename matches disallowed pattern: '{pattern}'")
    
    return violations


def is_binary_file(file_path: Path) -> bool:
    """Check if file is binary by looking for null bytes."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)  # Read first 8KB
            return b'\x00' in chunk
    except (OSError, PermissionError):
        return True  # Assume binary if we can't read
    
    # Also check common binary extensions
    binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz', 
                         '.so', '.dll', '.exe', '.bin', '.safetensors', '.pt', '.pth', '.onnx'}
    return file_path.suffix.lower() in binary_extensions


def check_file_content(file_path: Path) -> List[Tuple[int, str]]:
    """Check file content for secret patterns. Returns list of (line_number, violation)."""
    violations = []
    
    # Skip binary files
    if is_binary_file(file_path):
        return violations
    
    # Check if file is too large
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return violations  # Skip large files
    except OSError:
        return violations  # Skip if can't read
    
    # Check allowlist
    rel_path = str(file_path)
    allowed_patterns = []
    for allowed_path, patterns in ALLOWLIST.items():
        if allowed_path in rel_path:
            allowed_patterns.extend(patterns)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip comments in code files (reduce false positives)
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
                    # Still check for strong signatures even in comments
                    pass
                
                for pattern, message in SECRET_PATTERNS:
                    # Skip if pattern is in allowlist
                    pattern_key = pattern.split()[0].lower() if pattern.split() else ""
                    if any(allowed in pattern_key for allowed in allowed_patterns):
                        continue
                    
                    if re.search(pattern, line, re.IGNORECASE):
                        # Show context but truncate long lines
                        context = line.strip()[:80]
                        violations.append((line_num, f"{message}: {context}"))
    except (UnicodeDecodeError, PermissionError, OSError):
        # Skip binary files or files we can't read
        pass
    
    return violations


def scan_repository(repo_root: Path) -> List[Tuple[Path, List[str], List[Tuple[int, str]]]]:
    """Scan repository for violations. Returns list of (file_path, path_violations, content_violations)."""
    violations = []
    
    # Get all tracked files from git
    try:
        import subprocess
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        tracked_files = result.stdout.strip().split("\n")
        tracked_files = [f for f in tracked_files if f]  # Remove empty strings
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: scan all files if git is not available
        tracked_files = []
        for root, dirs, files in os.walk(repo_root):
            # Skip allowed directories
            dirs[:] = [d for d in dirs if d not in [a.lstrip(".") for a in ALLOWED_DIRS]]
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), repo_root)
                tracked_files.append(rel_path)
    
    for file_path_str in tracked_files:
        file_path = repo_root / file_path_str
        
        # Skip if file doesn't exist (might be deleted)
        if not file_path.exists():
            continue
        
        # Skip if in allowed directory
        if is_allowed_path(file_path):
            continue
        
        # Check path patterns
        path_violations = check_path_patterns(file_path)
        
        # Check filename patterns
        filename_violations = check_filename_patterns(file_path.name)
        path_violations.extend(filename_violations)
        
        # Check file content for secrets
        content_violations = check_file_content(file_path)
        
        if path_violations or content_violations:
            violations.append((file_path, path_violations, content_violations))
    
    return violations


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    print("🔍 Scanning repository for hygiene violations...")
    print(f"Repository root: {repo_root}")
    print()
    
    violations = scan_repository(repo_root)
    
    if violations:
        print("❌ VIOLATIONS FOUND:")
        print("=" * 70)
        for file_path, path_violations, content_violations in violations:
            rel_path = file_path.relative_to(repo_root)
            print(f"\n📄 {rel_path}")
            
            if path_violations:
                for violation in path_violations:
                    print(f"   ⚠️  {violation}")
            
            if content_violations:
                for line_num, violation in content_violations:
                    print(f"   ⚠️  Line {line_num}: {violation}")
        
        print()
        print("=" * 70)
        print()
        print("💡 RECOMMENDATIONS:")
        print("   - Remove or exclude files with violations")
        print("   - Ensure sensitive files are in .gitignore")
        print("   - Review files before committing")
        print()
        print("❌ Repository hygiene check FAILED")
        return 1
    else:
        print("✅ No violations found")
        print("✅ Repository hygiene check PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
