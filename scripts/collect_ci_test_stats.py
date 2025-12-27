#!/usr/bin/env python3
"""Collect test suite statistics from pytest runs.

Captures test count, runtime, and metadata for CI/metrics reporting.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_git_commit_hash() -> str:
    """Get short git commit hash, or 'unknown' if not available."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return 'unknown'


def run_pytest_and_parse() -> dict:
    """Run pytest and parse output for statistics."""
    try:
        result = subprocess.run(
            ['pytest', '-q'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        output = result.stdout + result.stderr
        
        # Parse final line: "XXX passed in Y.Ys" or "XXX passed, Y failed in Y.Ys"
        # Pattern: (\d+) passed(?:, (\d+) failed)? in ([\d.]+)s
        pattern = r'(\d+) passed(?:, (\d+) failed)? in ([\d.]+)s'
        match = re.search(pattern, output)
        
        if match:
            passed = int(match.group(1))
            failed = int(match.group(2)) if match.group(2) else 0
            runtime = float(match.group(3))
            
            return {
                'tests_passed': passed,
                'tests_failed': failed,
                'tests_total': passed + failed,
                'runtime_seconds': runtime,
                'exit_code': result.returncode,
            }
        else:
            # Fallback: try to find any number followed by "passed"
            passed_match = re.search(r'(\d+) passed', output)
            if passed_match:
                passed = int(passed_match.group(1))
                return {
                    'tests_passed': passed,
                    'tests_failed': 0,
                    'tests_total': passed,
                    'runtime_seconds': None,
                    'exit_code': result.returncode,
                }
    except Exception as e:
        return {
            'error': str(e),
            'tests_passed': None,
            'tests_failed': None,
            'tests_total': None,
            'runtime_seconds': None,
            'exit_code': None,
        }
    
    return {
        'error': 'Could not parse pytest output',
        'tests_passed': None,
        'tests_failed': None,
        'tests_total': None,
        'runtime_seconds': None,
        'exit_code': None,
    }


def generate_markdown_output(data: dict) -> str:
    """Generate Markdown formatted output."""
    lines = []
    
    lines.append("## Test Suite Statistics")
    lines.append("")
    lines.append(f"**Generated:** {data['timestamp']}")
    lines.append(f"**Commit:** `{data['commit_hash']}`")
    lines.append("")
    
    if data.get('error'):
        lines.append(f"⚠️ **Error:** {data['error']}")
        lines.append("")
    else:
        if data['tests_passed'] is not None:
            lines.append(f"- **Tests passed:** {data['tests_passed']}")
        if data['tests_failed'] is not None and data['tests_failed'] > 0:
            lines.append(f"- **Tests failed:** {data['tests_failed']}")
        if data['tests_total'] is not None:
            lines.append(f"- **Tests total:** {data['tests_total']}")
        if data['runtime_seconds'] is not None:
            lines.append(f"- **Runtime:** {data['runtime_seconds']:.2f} seconds")
        else:
            lines.append("- **Runtime:** Not available")
    
    lines.append("")
    
    return "\n".join(lines)


def main(output_json: str = None, output_md: str = None):
    """Main function."""
    # Run pytest and parse results
    stats = run_pytest_and_parse()
    
    # Add metadata
    stats['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    stats['commit_hash'] = get_git_commit_hash()
    
    # Generate Markdown output
    md_output = generate_markdown_output(stats)
    
    # Output to file or stdout
    if output_json:
        import json
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        print(f"JSON output written to {output_json}", file=sys.stderr)
    
    if output_md:
        with open(output_md, 'w', encoding='utf-8') as f:
            f.write(md_output)
        print(f"Markdown output written to {output_md}", file=sys.stderr)
    else:
        print(md_output)
    
    # Exit with pytest's exit code if available
    if stats.get('exit_code') is not None:
        sys.exit(stats['exit_code'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect test suite statistics')
    parser.add_argument('--json', type=str, help='Output JSON to file')
    parser.add_argument('--md', type=str, help='Output Markdown to file')
    
    args = parser.parse_args()
    
    main(output_json=args.json, output_md=args.md)

