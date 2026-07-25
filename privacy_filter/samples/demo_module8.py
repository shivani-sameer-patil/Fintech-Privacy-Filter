"""
Sample usage demo for Module 8: merger.py
"""

import json
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.merger import EntityMerger
from privacy_filter.detectors.regex_detector import Entity


def run_demo():
    print("==================================================")
    print("MODULE 8: ENTITY MERGER & OVERLAP RESOLUTION DEMO")
    print("==================================================")

    merger = EntityMerger()

    # Simulated outputs from multiple detector engines
    regex_entities = [
        Entity(type="CARD", text="4111 1111 1111 1111", start=100, end=119, confidence=1.0),
        Entity(type="CVV", text="4111", start=100, end=104, confidence=1.0),
        Entity(type="CVV", text="1111", start=105, end=109, confidence=1.0),
        Entity(type="EMAIL", text="shivani@gmail.com", start=150, end=167, confidence=1.0),
        Entity(type="UPI", text="shivani@gmail", start=150, end=163, confidence=1.0),
    ]

    spacy_entities = [
        Entity(type="PERSON", text="Shivani Patil", start=10, end=23, confidence=0.85),
        Entity(type="ORG", text="HDFC Bank", start=50, end=59, confidence=0.85),
    ]

    context_entities = [
        Entity(type="PAN", text="ABCDE1234F", start=70, end=80, confidence=1.0),
    ]

    print("\n[Input Unmerged Entity Candidates Count]:", len(regex_entities) + len(spacy_entities) + len(context_entities))
    print("[Overlapping Candidates]:")
    print("  1. Card '4111 1111 1111 1111' (span 100-119) vs CVV '4111' (span 100-104)")
    print("  2. Email 'shivani@gmail.com' (span 150-167) vs UPI 'shivani@gmail' (span 150-163)")

    merged = merger.merge(regex_entities, spacy_entities, context_entities)

    print(f"\n[Merged & Deduplicated Non-Overlapping Entities Count]: {len(merged)}")
    print("[Final Cleaned Entities Output (JSON)]:")
    print(json.dumps([e.to_dict() for e in merged], indent=4))


if __name__ == "__main__":
    run_demo()
