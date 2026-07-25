"""
Sample usage demo for Module 9: masker.py
"""

import json
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.masker import Masker
from privacy_filter.detectors.regex_detector import Entity


def run_demo():
    print("==================================================")
    print("MODULE 9: TEXT MASKER DEMO")
    print("==================================================")

    original_text = (
        "Customer Shivani Patil submitted PAN ABCDE1234F and email shivani@gmail.com. "
        "Bank account 123456789012 with IFSC SBIN0001234. Card: 4111 1111 1111 1111."
    )

    entities = [
        Entity(type="PERSON", text="Shivani Patil", start=9, end=22),
        Entity(type="PAN", text="ABCDE1234F", start=37, end=47),
        Entity(type="EMAIL", text="shivani@gmail.com", start=58, end=75),
        Entity(type="ACCOUNT_NUMBER", text="123456789012", start=90, end=102),
        Entity(type="IFSC", text="SBIN0001234", start=113, end=124),
        Entity(type="CARD", text="4111 1111 1111 1111", start=132, end=151),
    ]

    masker = Masker()
    result = masker.mask(original_text, entities)

    print("\n[Original Document Text]:")
    print(original_text)

    print("\n[Masked Document Text]:")
    print(result.masked_text)

    print("\n[Masking Summary Metrics JSON]:")
    print(json.dumps(result.to_dict(), indent=4))


if __name__ == "__main__":
    run_demo()
