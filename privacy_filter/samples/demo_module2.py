"""
Sample usage demo for Module 2: regex_detector.py
"""

import json
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.regex_detector import RegexDetector


def run_demo():
    sample_text = (
        "Customer Shivani Patil submitted PAN ABCDE1234F and email shivani@gmail.com. "
        "Bank account 123456789012 with IFSC SBIN0001234. Card: 4111 1111 1111 1111."
    )

    print("==================================================")
    print("MODULE 2: REGEX DETECTOR DEMO")
    print("==================================================")
    print("\n[Input Text]:")
    print(sample_text)
    print("\n[Detected Entities List (JSON schema)]: ")

    detector = RegexDetector()
    entities = detector.detect(sample_text)

    dict_output = [e.to_dict() for e in entities]
    print(json.dumps(dict_output, indent=4))

    print("\n[Offset Verification Check]:")
    for e in entities:
        extracted = sample_text[e.start:e.end]
        match_valid = extracted == e.text
        print(f"Type: {e.type:<15} | Span: ({e.start:<3}, {e.end:<3}) | Text: '{e.text}' | Match Valid: {match_valid}")


if __name__ == "__main__":
    run_demo()
