"""
Sample usage demo for Module 10: pipeline.py (End-to-End Master Pipeline Demo)
"""

import json
import sys
from pathlib import Path

# Force stdout UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline


def run_demo():
    print("==================================================")
    print("MODULE 10: FINTECH PRIVACY FILTER MASTER PIPELINE DEMO")
    print("==================================================")

    sample_documents = [
        (
            "1. Financial Email",
            (
                "Dear Customer Shivani Patil,\n"
                "Your PAN card ABCDE1234F and Aadhaar 2345 6789 0123 have been verified.\n"
                "Transaction of Rs. 15,000 sent from bank account 123456789012 with IFSC SBIN0001234.\n"
                "Card used: 4111 1111 1111 1111. Contact us at support@fintech.co.in or +91 9876543210.\n"
                "GSTIN: 27ABCDE1234F1Z5, CIN: U72200MH2020PTC123456. OTP is 482910."
            ),
        ),
        (
            "2. Multilingual Hindi Support Chat",
            (
                "नमस्ते, ग्राहक शिवानी पाटिल।\n"
                "आपका बैंक खाता संख्या: १२३४५६७८९०१२ और आधार: २३४५ ६७८९ ०১২३ सत्यापित किया गया है।\n"
                "संपर्क ईमेल: shivani@gmail.com या फोन: ९८७६५४३२१०।"
            ),
        ),
        (
            "3. Loan & Insurance Document",
            (
                "Loan Account Number: LN-1234-567890 under borrower Shivani Patil.\n"
                "Insurance Policy Number POL123456789 with premium payment UPI shivani@upi."
            ),
        ),
    ]

    pipeline = FinTechPrivacyPipeline()

    for label, doc_text in sample_documents:
        print(f"\n==================================================")
        print(f"DOCUMENT TYPE: {label}")
        print(f"==================================================")
        print("[RAW INPUT DOCUMENT]:")
        print(doc_text)

        result = pipeline.process(doc_text)

        print("\n[NORMALIZED TEXT]:")
        print(result.normalized_text)

        print("\n[SANITIZED MASKED TEXT]:")
        print(result.masked_text)

        print("\n[PIPELINE METRICS & DETECTED ENTITIES JSON]:")
        print(json.dumps(result.to_dict(), indent=4))


if __name__ == "__main__":
    run_demo()
