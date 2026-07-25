"""
Sample usage demo for Module 7: context_classifier.py
"""

import json
import sys
from pathlib import Path

# Force stdout UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.context_classifier import ContextClassifier
from privacy_filter.detectors.regex_detector import Entity


def run_demo():
    classifier = ContextClassifier()

    cases = [
        (
            "123456789012 alone in text",
            "Reference number 123456789012 found.",
            Entity(type="ACCOUNT_NUMBER", text="123456789012", start=17, end=29),
        ),
        (
            "English Account Context",
            "Bank Account Number: 123456789012",
            Entity(type="ACCOUNT_NUMBER", text="123456789012", start=21, end=33),
        ),
        (
            "Hindi Aadhaar Context",
            "आधार विवरण: 123456789012",
            Entity(type="ACCOUNT_NUMBER", text="123456789012", start=12, end=24),
        ),
        (
            "Kannada Loan Context",
            "ಸಾಲದ ಖಾತೆ: 123456789012",
            Entity(type="ACCOUNT_NUMBER", text="123456789012", start=11, end=23),
        ),
        (
            "Tamil Bank Account Context",
            "வங்கி கணக்கு: 123456789012",
            Entity(type="ACCOUNT_NUMBER", text="123456789012", start=14, end=26),
        ),
    ]

    print("==================================================")
    print("MODULE 7: CONTEXT CLASSIFIER DISAMBIGUATION DEMO")
    print("==================================================")

    for label, full_text, candidate in cases:
        result = classifier.classify_entity(candidate, full_text)
        print(f"\n[{label}]")
        print(f"Full Text   : '{full_text}'")
        print(f"Raw Input   : Type={candidate.type:<15} | Text='{candidate.text}'")
        print(f"Classified  : Type={result.type:<15} | Confidence={result.confidence} | Category={result.category}")


if __name__ == "__main__":
    run_demo()
