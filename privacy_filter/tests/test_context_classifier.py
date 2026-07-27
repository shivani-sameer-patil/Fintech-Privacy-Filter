"""
Unit tests for Module 7: context_classifier.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.context_classifier import ContextClassifier
from privacy_filter.detectors.regex_detector import Entity


class TestContextClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = ContextClassifier()

    def test_isolated_12_digit_number(self):
        text = "Reference code 123456789012 is stored in logs."
        candidate = Entity(
            type="ACCOUNT_NUMBER",
            text="123456789012",
            start=15,
            end=27,
            confidence=1.0,
        )
        res = self.classifier.classify_entity(candidate, text)
        self.assertEqual(res.type, "UNKNOWN_NUMERIC_ID")
        self.assertEqual(res.confidence, 0.50)

    def test_account_number_context_english(self):
        text = "Bank Account Number: 123456789012"
        candidate = Entity(
            type="ACCOUNT_NUMBER",
            text="123456789012",
            start=21,
            end=33,
            confidence=1.0,
        )
        res = self.classifier.classify_entity(candidate, text)
        self.assertEqual(res.type, "ACCOUNT_NUMBER")
        self.assertEqual(res.confidence, 0.95)

    def test_aadhaar_context_english(self):
        text = "Aadhaar UID: 123456789012"
        candidate = Entity(
            type="ACCOUNT_NUMBER",
            text="123456789012",
            start=13,
            end=25,
            confidence=1.0,
        )
        res = self.classifier.classify_entity(candidate, text)
        self.assertEqual(res.type, "AADHAAR")
        self.assertEqual(res.confidence, 1.0)

    def test_loan_account_context_english(self):
        text = "Loan Account Details: 123456789012"
        candidate = Entity(
            type="ACCOUNT_NUMBER",
            text="123456789012",
            start=22,
            end=34,
            confidence=1.0,
        )
        res = self.classifier.classify_entity(candidate, text)
        self.assertEqual(res.type, "LOAN_ACCOUNT")
        self.assertEqual(res.confidence, 0.95)

    def test_hindi_multilingual_context(self):
        # 1. Hindi Account
        text1 = "खाता संख्या: 123456789012"
        candidate1 = Entity(type="ACCOUNT_NUMBER", text="123456789012", start=13, end=25)
        res1 = self.classifier.classify_entity(candidate1, text1)
        self.assertEqual(res1.type, "ACCOUNT_NUMBER")

        # 2. Hindi Aadhaar
        text2 = "आधार कार्ड: 123456789012"
        candidate2 = Entity(type="ACCOUNT_NUMBER", text="123456789012", start=12, end=24)
        res2 = self.classifier.classify_entity(candidate2, text2)
        self.assertEqual(res2.type, "AADHAAR")

        # 3. Hindi Loan
        text3 = "ऋण विवरण: 123456789012"
        candidate3 = Entity(type="ACCOUNT_NUMBER", text="123456789012", start=10, end=22)
        res3 = self.classifier.classify_entity(candidate3, text3)
        self.assertEqual(res3.type, "LOAN_ACCOUNT")

    def test_kannada_multilingual_context(self):
        # 1. Kannada Account
        text1 = "ಖಾತೆ ಸಂಖ್ಯೆ: 123456789012"
        cand1 = Entity(type="ACCOUNT_NUMBER", text="123456789012", start=13, end=25)
        self.assertEqual(self.classifier.classify_entity(cand1, text1).type, "ACCOUNT_NUMBER")

        # 2. Kannada Aadhaar
        text2 = "ಆಧಾರ್ ಸಂಖ್ಯೆ: 123456789012"
        cand2 = Entity(type="ACCOUNT_NUMBER", text="123456789012", start=14, end=26)
        self.assertEqual(self.classifier.classify_entity(cand2, text2).type, "AADHAAR")

        # 3. Kannada Loan
        text3 = "ಸಾಲದ ಖಾತೆ: 123456789012"
        cand3 = Entity(type="ACCOUNT_NUMBER", text="123456789012", start=11, end=23)
        self.assertEqual(self.classifier.classify_entity(cand3, text3).type, "LOAN_ACCOUNT")

    def test_6digit_disambiguation(self):
        # Cheque
        text1 = "Cheque leaf number 000123"
        cand1 = Entity(type="CHEQUE_NUMBER", text="000123", start=19, end=25)
        self.assertEqual(self.classifier.classify_entity(cand1, text1).type, "CHEQUE_NUMBER")

        # OTP
        text2 = "Your OTP is 482910"
        cand2 = Entity(type="CHEQUE_NUMBER", text="482910", start=12, end=18)
        self.assertEqual(self.classifier.classify_entity(cand2, text2).type, "OTP")

        # MPIN
        text3 = "Enter your MPIN 123456"
        cand3 = Entity(type="CHEQUE_NUMBER", text="123456", start=16, end=22)
        self.assertEqual(self.classifier.classify_entity(cand3, text3).type, "MPIN")

    def test_isolated_6digit_number(self):
        text = "Chennai-600113 India"
        candidate = Entity(
            type="CHEQUE_NUMBER",
            text="600113",
            start=8,
            end=14,
            confidence=1.0,
        )
        res = self.classifier.classify_entity(candidate, text)
        self.assertEqual(res.type, "PINCODE")
        self.assertEqual(res.confidence, 0.50)


if __name__ == "__main__":
    unittest.main()
