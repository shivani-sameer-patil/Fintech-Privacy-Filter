"""
Sample usage demo for Module 1: regex_patterns.py
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.regex_patterns import (
    EntityCategory,
    EntityType,
    RegexPatternRegistry,
)


def run_demo():
    sample_text = """
    Dear Customer Shivani Patil,
    Your PAN card ABCDE1234F and Aadhaar 2345 6789 0123 have been verified.
    Transaction of Rs. 15,000 sent from account 123456789012 to UPI shivani@upi.
    IFSC: SBIN0001234. Card used: 4111 2222 3333 4444.
    Contact us at support@fintech.co.in or +91 9876543210.
    GSTIN: 27ABCDE1234F1Z5, CIN: U72200MH2020PTC123456.
    Security Alert: OTP is 482910 for login username: shivani_p.
    """

    print("==================================================")
    print("MODULE 1: REGEX PATTERN DETECTION DEMO")
    print("==================================================")
    print("\n[Input Text]:")
    print(sample_text.strip())
    print("\n[Detected Raw Matches]:")
    print("-" * 65)
    print(f"{'ENTITY TYPE':<18} | {'START':<6} | {'END':<6} | {'MATCHED TEXT'}")
    print("-" * 65)

    all_patterns = RegexPatternRegistry.get_all_patterns()

    total_matches = 0
    for entity_type, pattern_def in all_patterns.items():
        for match in pattern_def.compiled_regex.finditer(sample_text):
            print(
                f"{entity_type.value:<18} | {match.start():<6} | {match.end():<6} | '{match.group(0)}'"
            )
            total_matches += 1

    print("-" * 65)
    print(f"Total Sensitive Entity Candidates Found: {total_matches}\n")


if __name__ == "__main__":
    run_demo()
