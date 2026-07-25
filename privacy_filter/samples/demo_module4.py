"""
Sample usage demo for Module 4: spacy_detector.py
"""

import json
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.spacy_detector import SpacyDetector


def run_demo():
    sample_text = (
        "Shivani Patil submitted loan documents at HDFC Bank in Mumbai on 21st July 2026."
    )

    print("==================================================")
    print("MODULE 4: SPACY DETECTOR DEMO")
    print("==================================================")
    print("\n[Input Text]:")
    print(sample_text)

    detector = SpacyDetector()
    print(f"\nspaCy Engine Available: {detector.is_available}")

    entities = detector.detect(sample_text)
    print(f"\n[Detected Entities Count]: {len(entities)}")

    dict_output = [e.to_dict() for e in entities]
    print(json.dumps(dict_output, indent=4))


if __name__ == "__main__":
    run_demo()
