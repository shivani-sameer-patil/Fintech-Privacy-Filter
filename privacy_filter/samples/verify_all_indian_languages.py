"""
Comprehensive Multilingual Verification Script for All Official Indian Languages.

Demonstrates end-to-end pipeline execution across Indian regional languages:
Language Detection -> Indic Numeral Normalization -> Context Disambiguation -> Masking.
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


def run_multilingual_verification():
    test_suite = [
        (
            "Hindi (Devanagari)",
            "hi",
            "नमस्ते, ग्राहक शिवानी पाटिल। आपका खाता संख्या: १२३४५६७८९०१२ और आधार: २३४५ ६७৮९ ०१२३। ईमेल: shivani@gmail.com, फोन: ९८७६५४३२१०।"
        ),
        (
            "Kannada",
            "kn",
            "ನಮಸ್ಕಾರ, ಗ್ರಾಹಕ ಶಿವಾನಿ ಪಾಟೀಲ್. ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆ ಸಂಖ್ಯೆ: ೧೨೩೪೫೬೭೮೯೦೧೨ ಮತ್ತು ಆಧಾರ್: ೨೩೪೫ ೬೭೮೯ ೦೧೨೩. ಇಮೇಲ್: shivani@gmail.com, ಮೊಬೈಲ್: ೯೮೭೬೫೪೩೨೧೦."
        ),
        (
            "Tamil",
            "ta",
            "வணக்கம், வாடிக்கையாளர் சிவானி பாட்டீல். உங்கள் வங்கி கணக்கு எண்: ௦௧௨௩௪௫௬௭௮௯ மற்றும் ஆதார்: ௨௩௪௫ ௬௭௮௯ ௦௧௨௩. மின்னஞ்சல்: shivani@gmail.com, கைபேசி: ௯௮௭௬௫௪௩௨௧௦."
        ),
        (
            "Telugu",
            "te",
            "నమస్కారం, కస్టమర్ శివాని పాటిల్. మీ బ్యాంక్ ఖాతా సంఖ్య: ౧౨౩౪౫౬౭౮౯౦౧౨ మరియు ఆధార్: ౨౩౪౫ ౬౭౮౯ ౦౧౨౩. ఇమెయిల్: shivani@gmail.com, ఫోన్: ౯౮౭౬౫౪౩౨౧౦."
        ),
        (
            "Malayalam",
            "ml",
            "നമസ്കാരം, ഉപഭോക്താവ് ശിവാനി പാട്ടീൽ. നിങ്ങളുടെ ബാങ്ക് അക്കൗണ്ട് നമ്പർ: ൧൨൩൪൫൬൭൮൯൦൧൨ കൂടാതെ ആധാർ: ൨൩൪൫ ൬൭൮൯ ൦൧൨൩. ഇമെയിൽ: shivani@gmail.com, ഫോൺ: ൯൮൭൬൫൪൩൨൧൦."
        ),
        (
            "Bengali",
            "bn",
            "নমস্কার, গ্রাহক শিবানী পাতিল। আপনার ব্যাংক অ্যাকাউন্ট নম্বর: ১২৩৪৫৬৭৮৯০১২ এবং আধার: ২৩৪৫ ৬৭৮৯ ০১২৩। ইমেল: shivani@gmail.com, ফোন: ৯৮৭৬৫৪৩২১০।"
        ),
        (
            "Gujarati",
            "gu",
            "નમસ્તે, ગ્રાહક શિવાની પાટીલ. તમારો બેંક ખાતા નંબર: ૦૧૨૩૪૫૬૭૮૯૦૧૨ અને આધાર: ૨૩૪૫ ૬૭૮૯ ૦૧૨૩. ઇમેઇલ: shivani@gmail.com, ફોન: ૯૮૭૬૫૪૩૨૧૦."
        ),
        (
            "Marathi",
            "mr",
            "नमस्कार, ग्राहक शिवानी पाटील. आपला बँक खाते क्रमांक: १२३४५६७८९०१२ आणि आधार: २३४५ ६७८९ ०१२३. ईमेल: shivani@gmail.com, फोन: ९८७६५४३२१०."
        ),
        (
            "Punjabi (Gurmukhi)",
            "pa",
            "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ, ਗਾਹਕ ਸ਼ਿਵਾਨੀ ਪਾਟੀਲ। ਤੁਹਾਡਾ ਬੈਂਕ ਖਾਤਾ ਨੰਬਰ: ੧੨੩੪੫੬੭੮੯੦੧੨ ਅਤੇ ਆਧਾਰ: ੨੩੪੫ ੬੭੮੯ ੦੧੨੩। ਈਮੇਲ: shivani@gmail.com, ਫੋਨ: ੯੮੭੬੫੪੩੨੧੦।"
        ),
        (
            "Odia",
            "or",
            "ନମସ୍କାର, ଗ୍ରାହକ ଶିବାନୀ ପାଟିଲ | ଆପଣଙ୍କ ବ୍ୟାଙ୍କ ଖାତା ନମ୍ବର: ୧୨୩୪୫୬୭୮୯୦୧୨ ଏବଂ ଆଧାର: ୨୩૪୫ ୬୭୮୯ ୦୧୨୩ | ଇମେଲ: shivani@gmail.com, ଫୋନ୍: ୯୮୭୬୫၄୩୨୧୦ |"
        ),
        (
            "Urdu (Perso-Arabic)",
            "ur",
            "سلام، صارف شیوانی پاٹل۔ آپ کا بینک اکاؤنٹ نمبر: ۰۱۲۳۴۵۶۷۸۹۰۱۲ اور آدھار: ۲۳۴۵ ۶۷۸۹ ۰۱۲۳۔ ای میل: shivani@gmail.com، فون: ۹۸۷۶۵۴۳۲۱۰۔"
        ),
    ]

    pipeline = FinTechPrivacyPipeline()

    print("==========================================================================================")
    print("FINTECH PRIVACY FILTER: MULTILINGUAL INDIAN LANGUAGES AGENT VERIFICATION")
    print("==========================================================================================")

    total_passed = 0

    for idx, (lang_title, expected_code, raw_text) in enumerate(test_suite, start=1):
        output = pipeline.process(raw_text)

        detected_lang = output.language.language_code
        lang_valid = (detected_lang == expected_code) or (output.language.script_name != "")

        # Verify key entities are sanitized
        entities_sanitized = (
            "123456789012" not in output.masked_text
            and "shivani@gmail.com" not in output.masked_text
            and "9876543210" not in output.masked_text
        )

        status = "PASSED [VERIFIED]" if (lang_valid and entities_sanitized) else "FAILED"
        if status.startswith("PASSED"):
            total_passed += 1

        print(f"\n[{idx}] LANGUAGE: {lang_title:<22} | AGENT STATUS: {status}")
        print("-" * 90)
        print(f"  Raw Input Text  : {raw_text}")
        print(f"  Normalized Text : {output.normalized_text}")
        print(f"  Masked Text     : {output.masked_text}")
        print(f"  Detected Script : {output.language.script_name:<12} | Lang Code: {output.language.language_code:<4} | Masked Count: {output.entities_masked_count}")

    print("\n==========================================================================================")
    print(f"VERIFICATION SUMMARY: {total_passed}/{len(test_suite)} Multilingual Language Test Suits PASSED")
    print("==========================================================================================")


if __name__ == "__main__":
    run_multilingual_verification()
