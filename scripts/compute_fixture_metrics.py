#!/usr/bin/env python3
"""Compute accuracy metrics from synthetic fixture data.

Reads tests/fixtures/sample_chats.jsonl, runs analysis on each chat,
and compares expected vs actual risk levels.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.detection.engine import DetectionEngine
from app.utils.constants import RiskLevel


def load_fixtures(fixture_path: Path):
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


def compute_metrics(fixture_path: Path):
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
        
        # Update counters
        counts[expected_level]['total'] += 1
        if actual_level == expected_level:
            counts[expected_level]['correct'] += 1
    
    # Calculate metrics
    total_chats = sum(c['total'] for c in counts.values())
    total_correct = sum(c['correct'] for c in counts.values())
    
    # Print markdown-ready output
    print("## Accuracy Metrics (Synthetic Fixtures)")
    print()
    print(f"**Total test chats:** {total_chats}")
    print()
    print("### Per-Level Accuracy")
    print()
    
    for level in [RiskLevel.GREEN, RiskLevel.YELLOW, RiskLevel.RED]:
        level_name = level.value.upper()
        correct = counts[level]['correct']
        total = counts[level]['total']
        if total > 0:
            accuracy_pct = (correct / total) * 100
            print(f"- **{level_name}**: {correct}/{total} ({accuracy_pct:.1f}%)")
        else:
            print(f"- **{level_name}**: 0/0 (N/A)")
    
    print()
    if total_chats > 0:
        overall_accuracy = (total_correct / total_chats) * 100
        print(f"**Overall accuracy:** {total_correct}/{total_chats} ({overall_accuracy:.1f}%)")
    else:
        print("**Overall accuracy:** N/A (no test chats)")
    
    print()
    print("> **Note:** These metrics are computed from synthetic test fixtures. Real-world accuracy may vary.")


if __name__ == '__main__':
    # Get fixture path
    repo_root = Path(__file__).parent.parent
    fixture_path = repo_root / 'tests' / 'fixtures' / 'sample_chats.jsonl'
    
    if not fixture_path.exists():
        print(f"Error: Fixture file not found: {fixture_path}", file=sys.stderr)
        sys.exit(1)
    
    compute_metrics(fixture_path)

