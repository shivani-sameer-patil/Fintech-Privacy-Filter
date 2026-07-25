"""
Sample usage demo for Module 3: presidio_detector.py
"""

import json
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.presidio_detector import PresidioDetector


def run_demo():
    sample_text = (
        "Customer Shivani Patil living in Mumbai sent an email to shivani@gmail.com "
        "and called phone +91 9876543210 regarding credit card 4111 1111 1111 1111."
    )

    print("==================================================")
    print("MODULE 3: PRESIDIO DETECTOR DEMO")
    print("==================================================")
    print("\n[Input Text]:")
    print(sample_text)

    detector = PresidioDetector()
    print(f"\nPresidio Engine Available: {detector.is_available}")

    entities = detector.detect(sample_text)
    print(f"\n[Detected Entities Count]: {len(entities)}")

    dict_output = [e.to_dict() for e in entities]
    print(json.dumps(dict_output, indent=4))


if __name__ == "__main__":
    run_demo()
