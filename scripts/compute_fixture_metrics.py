#!/usr/bin/env python3
"""Compute accuracy metrics from synthetic fixture data.

Reads tests/fixtures/sample_chats.jsonl, runs analysis on each chat,
and compares expected vs actual risk levels.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.detection.engine import DetectionEngine
from app.utils.constants import RiskLevel


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


def load_fixtures(fixture_path: Path) -> List[dict]:
    """Load JSONL fixture file."""
    chats = []
    with open(fixture_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                chats.append(json.loads(line))
    return chats


def normalize_risk_level(risk_str: str) -> str:
    """Normalize risk level string to lowercase."""
    return risk_str.lower().strip()


def build_confusion_matrix(results: List[dict]) -> Dict[str, Dict[str, int]]:
    """Build confusion matrix from results."""
    matrix = {
        'GREEN': {'GREEN': 0, 'YELLOW': 0, 'RED': 0},
        'YELLOW': {'GREEN': 0, 'YELLOW': 0, 'RED': 0},
        'RED': {'GREEN': 0, 'YELLOW': 0, 'RED': 0},
    }
    
    for result in results:
        expected = result['expected'].value.upper()
        actual = result['actual'].value.upper()
        matrix[expected][actual] += 1
    
    return matrix


def compute_metrics(fixture_path: Path, output_json: Optional[str] = None, output_md: Optional[str] = None):
    """Compute accuracy metrics from fixture data."""
    chats = load_fixtures(fixture_path)
    
    # Initialize detection engine
    engine = DetectionEngine(use_ml=True)
    
    # Counters per level
    counts = {
        RiskLevel.GREEN: {'correct': 0, 'total': 0},
        RiskLevel.YELLOW: {'correct': 0, 'total': 0},
        RiskLevel.RED: {'correct': 0, 'total': 0},
    }
    
    # Store all results for confusion matrix and validation
    all_results = []
    help_section_red_only_count = 0
    help_section_non_red_count = 0
    evidence_violations = 0
    
    # Process each chat
    for chat in chats:
        expected_str = normalize_risk_level(chat.get('risk_expected', ''))
        chat_text = chat.get('chat_text', '')
        
        if not expected_str or not chat_text:
            continue
        
        # Map expected string to RiskLevel enum
        try:
            expected_level = RiskLevel(expected_str)
        except ValueError:
            continue
        
        # Run analysis
        result = engine.analyze(chat_text)
        actual_level = result.risk_level
        
        # Store result for confusion matrix
        all_results.append({
            'expected': expected_level,
            'actual': actual_level,
            'explanation': result.explanation,
            'matches': result.matches,
        })
        
        # Update counters
        counts[expected_level]['total'] += 1
        if actual_level == expected_level:
            counts[expected_level]['correct'] += 1
        
        # Check "Need Immediate Help?" appears only for RED
        explanation_lower = result.explanation.lower()
        has_help_section = 'need immediate help' in explanation_lower or 'immediate help' in explanation_lower
        
        if has_help_section:
            if actual_level == RiskLevel.RED:
                help_section_red_only_count += 1
            else:
                help_section_non_red_count += 1
        
        # Check evidence-based behaviors (approximate)
        # If explanation mentions "observed behavior" but matches is empty, flag it
        has_observed_behavior = 'observed behavior' in explanation_lower or 'observed behaviors' in explanation_lower
        has_matches = result.matches and any(result.matches.values())
        
        if has_observed_behavior and not has_matches:
            evidence_violations += 1
    
    # Calculate metrics
    total_chats = sum(c['total'] for c in counts.values())
    total_correct = sum(c['correct'] for c in counts.values())
    
    # Build confusion matrix
    confusion_matrix = build_confusion_matrix(all_results)
    
    # Get metadata
    commit_hash = get_git_commit_hash()
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Prepare output data
    output_data = {
        'timestamp': timestamp,
        'commit_hash': commit_hash,
        'total_chats': total_chats,
        'overall_accuracy': (total_correct / total_chats * 100) if total_chats > 0 else 0.0,
        'per_level_accuracy': {},
        'confusion_matrix': confusion_matrix,
        'validation_checks': {
            'help_section_red_only': help_section_red_only_count,
            'help_section_non_red_violations': help_section_non_red_count,
            'evidence_violations_approximate': evidence_violations,
        }
    }
    
    for level in [RiskLevel.GREEN, RiskLevel.YELLOW, RiskLevel.RED]:
        level_name = level.value.upper()
        correct = counts[level]['correct']
        total = counts[level]['total']
        if total > 0:
            accuracy_pct = (correct / total) * 100
            output_data['per_level_accuracy'][level_name] = {
                'correct': correct,
                'total': total,
                'accuracy_pct': accuracy_pct
            }
        else:
            output_data['per_level_accuracy'][level_name] = {
                'correct': 0,
                'total': 0,
                'accuracy_pct': None
            }
    
    # Generate Markdown output
    md_output = generate_markdown_output(output_data)
    
    # Output to file or stdout
    if output_json:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        print(f"JSON output written to {output_json}", file=sys.stderr)
    
    if output_md:
        with open(output_md, 'w', encoding='utf-8') as f:
            f.write(md_output)
        print(f"Markdown output written to {output_md}", file=sys.stderr)
    else:
        print(md_output)


def generate_markdown_output(data: dict) -> str:
    """Generate Markdown formatted output."""
    lines = []
    
    lines.append("## Accuracy Metrics (Synthetic Fixtures)")
    lines.append("")
    lines.append(f"**Generated:** {data['timestamp']}")
    lines.append(f"**Commit:** `{data['commit_hash']}`")
    lines.append("")
    lines.append(f"**Total test chats:** {data['total_chats']}")
    lines.append("")
    lines.append("### Per-Level Accuracy")
    lines.append("")
    
    for level_name in ['GREEN', 'YELLOW', 'RED']:
        level_data = data['per_level_accuracy'][level_name]
        if level_data['accuracy_pct'] is not None:
            lines.append(f"- **{level_name}**: {level_data['correct']}/{level_data['total']} ({level_data['accuracy_pct']:.1f}%)")
        else:
            lines.append(f"- **{level_name}**: 0/0 (N/A)")
    
    lines.append("")
    lines.append(f"**Overall accuracy:** {data['overall_accuracy']:.1f}%")
    lines.append("")
    
    # Confusion matrix
    lines.append("### Confusion Matrix")
    lines.append("")
    lines.append("| Expected → Actual | GREEN | YELLOW | RED |")
    lines.append("|-------------------|-------|--------|-----|")
    
    for expected in ['GREEN', 'YELLOW', 'RED']:
        row = [expected]
        for actual in ['GREEN', 'YELLOW', 'RED']:
            row.append(str(data['confusion_matrix'][expected][actual]))
        lines.append("| " + " | ".join(row) + " |")
    
    lines.append("")
    
    # Validation checks
    lines.append("### Validation Checks")
    lines.append("")
    lines.append(f"- **\"Need Immediate Help?\" appears only for RED:** ✅ {data['validation_checks']['help_section_red_only']} cases")
    if data['validation_checks']['help_section_non_red_violations'] > 0:
        lines.append(f"  - ⚠️ Violations (non-RED with help section): {data['validation_checks']['help_section_non_red_violations']}")
    else:
        lines.append("  - ✅ No violations found")
    
    lines.append(f"- **Evidence-based behaviors (approximate):** {data['validation_checks']['evidence_violations_approximate']} potential violations")
    lines.append("  - Note: This is an approximate check based on text matching. Full validation requires parsing natural language explanations.")
    lines.append("")
    
    lines.append("> **Note:** These metrics are computed from synthetic test fixtures. Real-world accuracy may vary.")
    
    return "\n".join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute accuracy metrics from test fixtures')
    parser.add_argument('--json', type=str, help='Output JSON to file')
    parser.add_argument('--md', type=str, help='Output Markdown to file')
    
    args = parser.parse_args()
    
    # Get fixture path
    repo_root = Path(__file__).parent.parent
    fixture_path = repo_root / 'tests' / 'fixtures' / 'sample_chats.jsonl'
    
    if not fixture_path.exists():
        print(f"Error: Fixture file not found: {fixture_path}", file=sys.stderr)
        sys.exit(1)
    
    compute_metrics(fixture_path, output_json=args.json, output_md=args.md)
