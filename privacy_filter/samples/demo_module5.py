"""
Sample usage demo for Module 5: language_detector.py
"""

import json
import sys
from pathlib import Path

# Force stdout UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.language_detector import LanguageDetector


def run_demo():
    samples = [
        "Dear Customer, please verify your PAN card ABCDE1234F.",
        "नमस्ते, कृपया अपना खाता संख्या और आधार कार्ड नंबर दर्ज करें।",
        "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆ ಸಂಖ್ಯೆ ಮತ್ತು ಆಧಾರ್ ಸಂಖ್ಯೆಯನ್ನು ಒದಗಿಸಿ.",
        "உங்கள் வங்கி கணக்கு எண் மற்றும் ஆதார் எண்ணை சரிபார்க்கவும்.",
        "మీ బ్యాంక్ ఖాతా సంఖ్య మరియు ఆధార్ సంఖ్యను నమోదు చేయండి.",
        "আপনার ব্যাঙ্ক অ্যাকাউন্ট নম্বর এবং আধার নম্বর যাচাই করুন।",
    ]

    print("==================================================")
    print("MODULE 5: MULTILINGUAL LANGUAGE DETECTOR DEMO")
    print("==================================================")

    detector = LanguageDetector()

    for idx, text in enumerate(samples, start=1):
        result = detector.detect(text)
        print(f"\n[Sample {idx} Input]: '{text}'")
        print("[Detection Result JSON]:")
        print(json.dumps(result.to_dict(), indent=4))


if __name__ == "__main__":
    run_demo()
