#!/usr/bin/env python3
"""
Repository Hygiene Checker

Scans the repository for disallowed patterns that should not be committed
to the public repository. This includes internal prompts, debug prompts,
private notes, and other internal development artifacts.

Usage:
    python scripts/repo_hygiene_check.py

Exit codes:
    0: No violations found
    1: Violations found
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Disallowed filename patterns (case-insensitive)
DISALLOWED_PATTERNS = [
    "prompt",
    "debug_prompt",
    "private",
    "notes",
    "scratch",
    "local",  # Except .local/ directory itself
]

# Allowed directories (excluded from scanning)
ALLOWED_DIRS = [
    ".local",  # Local-only directory is allowed
    ".git",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".streamlit",
    "dist",
    "build",
    "models",  # Model files are large and gitignored
]

# Allowed file extensions (these are typically safe)
ALLOWED_EXTENSIONS = [
    ".py",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".sh",
    ".spec",
    ".gitignore",
    ".gitkeep",
    ".LICENSE",
]


def is_allowed_path(file_path: Path) -> bool:
    """Check if a file path should be excluded from scanning."""
    # Check if path is in an allowed directory
    for allowed_dir in ALLOWED_DIRS:
        if allowed_dir in file_path.parts:
            return True
    
    # Check if file has allowed extension
    if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
        # But still check filename for disallowed patterns
        return False
    
    return False


def check_filename(filename: str) -> List[str]:
    """Check if filename contains disallowed patterns."""
    violations = []
    filename_lower = filename.lower()
    
    for pattern in DISALLOWED_PATTERNS:
        if pattern in filename_lower:
            # Special case: .local/ directory is allowed
            if pattern == "local" and ".local" in filename_lower:
                continue
            violations.append(f"Filename contains disallowed pattern: '{pattern}'")
    
    return violations


def scan_repository(repo_root: Path) -> List[Tuple[Path, List[str]]]:
    """Scan repository for violations."""
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
        
        # Check filename
        filename_violations = check_filename(file_path.name)
        if filename_violations:
            violations.append((file_path, filename_violations))
    
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
        for file_path, file_violations in violations:
            rel_path = file_path.relative_to(repo_root)
            print(f"\n📄 {rel_path}")
            for violation in file_violations:
                print(f"   ⚠️  {violation}")
        print()
        print("=" * 70)
        print()
        print("💡 RECOMMENDATIONS:")
        print("   - Move internal files to .local/ directory")
        print("   - Ensure .local/ is in .gitignore")
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

