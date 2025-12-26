#!/usr/bin/env python3
"""CLI script to generate test chat corpus.

Usage:
    python3 scripts/generate_test_chats.py --seed 1337 --count 50 --out tests/fixtures/generated_chats.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.testing.chat_corpus_generator import ChatCorpusGenerator


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate test chat corpus")
    parser.add_argument(
        "--seed",
        type=int,
        default=1337,
        help="Random seed for deterministic generation (default: 1337)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of chats per risk level (default: 50)"
    )
    parser.add_argument(
        "--out",
        type=str,
        default="tests/fixtures/generated_chats.jsonl",
        help="Output file path (default: tests/fixtures/generated_chats.jsonl)"
    )
    
    args = parser.parse_args()
    
    # Generate corpus
    generator = ChatCorpusGenerator(seed=args.seed)
    corpus = generator.generate_corpus(count_per_level=args.count)
    
    # Write to file (JSONL format: one JSON object per line)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for chat in corpus:
            f.write(json.dumps(chat, ensure_ascii=False) + '\n')
    
    print(f"Generated {len(corpus)} chats ({args.count} per level)")
    print(f"Written to: {output_path}")
    print(f"Seed: {args.seed}")


if __name__ == "__main__":
    main()

