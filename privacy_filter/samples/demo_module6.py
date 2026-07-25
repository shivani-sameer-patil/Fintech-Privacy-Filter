"""
Sample usage demo for Module 6: indic_normalizer.py
"""

import sys
from pathlib import Path

# Force stdout UTF-8 encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.indic_normalizer import IndicNormalizer


def run_demo():
    samples = [
        ("Hindi (Devanagari)", "खाता संख्या: १२३४५६७८९०१२"),
        ("Kannada", "ಖಾತೆ ಸಂಖ್ಯೆ: ೧೨೩೪೫೬೭೮೯೦೧೨"),
        ("Bengali", "অ্যাকাউন্ট নম্বর: ১২৩৪৫৬৭৮৯০১২"),
        ("Tamil", "வங்கி கணக்கு: ௦௧௨௩௪௫௬௭௮௯"),
        ("Telugu", "ఖాతా సంఖ్య: ౦౧౨౩౪౫౬౭౮౯"),
        ("Malayalam", "അക്കൗണ്ട്: ൦൧൨൩൪൫൬൭൮൯"),
        ("Gujarati", "ખાતા નંબર: ૦૧૨૩૪૫૬૭૮૯"),
        ("Urdu (Perso-Arabic)", "کھاتہ نمبر: ۰۱۲۳۴۵۶۷۸۹"),
    ]

    print("==================================================")
    print("MODULE 6: INDIC NUMERAL NORMALIZER DEMO")
    print("==================================================")

    normalizer = IndicNormalizer()

    for lang_label, text in samples:
        normalized = normalizer.normalize_text(text)
        print(f"\n[{lang_label} Original]  : {text}")
        print(f"[{lang_label} Normalized]: {normalized}")


if __name__ == "__main__":
    run_demo()
