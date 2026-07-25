"""
Unit tests for Module 5: language_detector.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.language_detector import (
    LanguageDetector,
    LanguageResult,
)


class TestLanguageDetector(unittest.TestCase):

    def setUp(self):
        self.detector = LanguageDetector()

    def test_empty_and_whitespace_input(self):
        res1 = self.detector.detect("")
        self.assertEqual(res1.language_code, "en")
        self.assertEqual(res1.language_name, "English")

        res2 = self.detector.detect("   \n\t  ")
        self.assertEqual(res2.language_code, "en")

    def test_english_detection(self):
        text = "Hello, please find attached loan statement and bank account details."
        res = self.detector.detect(text)
        self.assertEqual(res.language_code, "en")
        self.assertEqual(res.script_name, "Latin")
        self.assertGreater(res.confidence, 0.8)

    def test_hindi_detection(self):
        text = "नमस्ते, कृपया अपना खाता संख्या और आधार कार्ड नंबर भेजें।"
        res = self.detector.detect(text)
        self.assertEqual(res.language_code, "hi")
        self.assertEqual(res.script_name, "Devanagari")
        self.assertEqual(res.language_name, "Hindi")

    def test_kannada_detection(self):
        text = "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆ ಸಂಖ್ಯೆ ಮತ್ತು ಆಧಾರ್ ಸಂಖ್ಯೆಯನ್ನು ಒದಗಿಸಿ."
        res = self.detector.detect(text)
        self.assertEqual(res.language_code, "kn")
        self.assertEqual(res.script_name, "Kannada")
        self.assertEqual(res.language_name, "Kannada")

    def test_tamil_detection(self):
        text = "உங்கள் வங்கி கணக்கு எண் மற்றும் ஆதார் எண்ணை சரிபார்க்கவும்."
        res = self.detector.detect(text)
        self.assertEqual(res.language_code, "ta")
        self.assertEqual(res.script_name, "Tamil")
        self.assertEqual(res.language_name, "Tamil")

    def test_telugu_detection(self):
        text = "మీ బ్యాంక్ ఖాతా సంఖ్య మరియు ఆధార్ సంఖ్యను నమోదు చేయండి."
        res = self.detector.detect(text)
        self.assertEqual(res.language_code, "te")
        self.assertEqual(res.script_name, "Telugu")
        self.assertEqual(res.language_name, "Telugu")

    def test_bengali_detection(self):
        text = "আপনার ব্যাঙ্ক অ্যাকাউন্ট নম্বর এবং আধার নম্বর যাচাই করুন।"
        res = self.detector.detect(text)
        self.assertEqual(res.language_code, "bn")
        self.assertEqual(res.script_name, "Bengali")
        self.assertEqual(res.language_name, "Bengali")

    def test_result_to_dict(self):
        res = LanguageResult(
            language_code="hi",
            language_name="Hindi",
            confidence=0.985,
            script_name="Devanagari",
        )
        expected = {
            "language_code": "hi",
            "language_name": "Hindi",
            "confidence": 0.985,
            "script_name": "Devanagari",
        }
        self.assertEqual(res.to_dict(), expected)


if __name__ == "__main__":
    unittest.main()
