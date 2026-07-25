"""
Unit tests for the Multilingual Keyword Classifier and Detector.
"""

import sys
import unittest
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.multilingual_keyword_detector import (
    MultilingualKeywordClassifier,
    MultilingualKeywordDetector,
)
from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline
from privacy_filter.detectors.regex_detector import Entity


class TestMultilingualKeywordClassifier(unittest.TestCase):

    def setUp(self):
        # By default, classifier is trained on MULTILINGUAL_KEYWORDS
        self.classifier = MultilingualKeywordClassifier()

    def test_default_prediction_english(self):
        # "otp" keyword -> should predict OTP
        best_class, conf = self.classifier.predict("Your transaction otp verification")
        self.assertEqual(best_class, "OTP")
        self.assertTrue(conf > 0.5)

    def test_default_prediction_hindi(self):
        # "आधार" keyword -> should predict AADHAAR
        best_class, conf = self.classifier.predict("यहाँ अपना आधार विवरण दें")
        self.assertEqual(best_class, "AADHAAR")
        self.assertTrue(conf > 0.5)

    def test_custom_training(self):
        classifier = MultilingualKeywordClassifier(keyword_dict={})  # empty start
        training_samples = [
            ("please enter security mpin pin", "MPIN"),
            ("your policy premium insurance details", "POLICY_NUMBER"),
            ("the bank savings account number is", "ACCOUNT_NUMBER"),
        ]
        classifier.train(training_samples)

        # Test MPIN prediction
        best_class, conf = classifier.predict("MPIN code")
        self.assertEqual(best_class, "MPIN")

        # Test POLICY_NUMBER prediction
        best_class, conf = classifier.predict("my policy number is")
        self.assertEqual(best_class, "POLICY_NUMBER")


class TestMultilingualKeywordDetector(unittest.TestCase):

    def setUp(self):
        self.detector = MultilingualKeywordDetector()

    def test_detect_otp_english(self):
        text = "Your security OTP is 482910."
        entities = self.detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].type, "OTP")
        self.assertEqual(entities[0].text, "482910")

    def test_detect_aadhaar_hindi(self):
        text = "विवरण में आधार संख्या १२३४५६७८९०१२ है।"
        # Normalize first since detector expects normalized ASCII digits (handled in pipeline)
        from privacy_filter.detectors.indic_normalizer import IndicNormalizer

        normalized = IndicNormalizer().normalize_text(text)
        entities = self.detector.detect(normalized)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].type, "AADHAAR")
        self.assertEqual(entities[0].text, "123456789012")

    def test_format_validation_prevention(self):
        # 1234 is not a valid Aadhaar length (requires 12 digits)
        text = "My Aadhaar card number is 1234."
        entities = self.detector.detect(text)
        # Even if Aadhaar is predicted, validation should filter it out because length is 4 digits
        aadhaar_entities = [e for e in entities if e.type == "AADHAAR"]
        self.assertEqual(len(aadhaar_entities), 0)


class TestPipelineKeywordIntegration(unittest.TestCase):

    def test_pipeline_end_to_end(self):
        pipeline = FinTechPrivacyPipeline()

        # Sentence in Hindi with Hindi keyword + numeric OTP
        raw_text = "कृपया अपना ओटीपी ९८७६५४ दर्ज करें।"
        output = pipeline.process(raw_text)

        # Should normalize OTP to ASCII and mask it with [OTP]
        self.assertIn("[OTP]", output.masked_text)
        self.assertNotIn("987654", output.masked_text)
        self.assertEqual(output.entities_masked_count, 1)

    def test_indian_amount_normalization_and_masking(self):
        pipeline = FinTechPrivacyPipeline()
        text = "Opening Balance: Rs. 1,45,000.00"
        output = pipeline.process(text)
        self.assertIn("[AMOUNT]", output.masked_text)
        self.assertNotIn("1,45,000.00", output.masked_text)

        text_hindi = "स्वीकृत राशि: रु. २५,००,०००"
        output_hindi = pipeline.process(text_hindi)
        self.assertIn("[AMOUNT]", output_hindi.masked_text)
        self.assertNotIn("25,00,000", output_hindi.masked_text)

        # Test case: Amount in words
        text_words = "The total charges are Three thousand two hunderd twenty one rupees."
        output_words = pipeline.process(text_words)
        self.assertIn("[AMOUNT]", output_words.masked_text)
        self.assertNotIn("Three thousand two hunderd twenty one rupees", output_words.masked_text)

        # Test case: Amount with arbitrary comma separators
        text_commas = "Balance is Rs. 1,2,3,4,5.00"
        output_commas = pipeline.process(text_commas)
        self.assertIn("[AMOUNT]", output_commas.masked_text)
        self.assertNotIn("1,2,3,4,5.00", output_commas.masked_text)

        # Test case: Mix of digits and words (e.g. 5 lakh rupees / ५ हजार रुपये)
        text_mixed = "ऋण राशि ५ हजार रुपये है"
        output_mixed = pipeline.process(text_mixed)
        self.assertIn("[AMOUNT]", output_mixed.masked_text)
        self.assertNotIn("५ हजार रुपये", output_mixed.masked_text)


    def test_swift_false_positive_prevention(self):
        pipeline = FinTechPrivacyPipeline()
        # Normal uppercase words should NOT be matched as SWIFT codes
        text = "SECURITY & CREDENTIALS AUDIT LOG"
        output = pipeline.process(text)
        self.assertNotIn("[SWIFT]", output.masked_text)

    def test_micr_disambiguation(self):
        pipeline = FinTechPrivacyPipeline()
        text = "Branch MICR Code: 400002015"
        output = pipeline.process(text)
        self.assertIn("[MICR]", output.masked_text)
        self.assertNotIn("400002015", output.masked_text)


if __name__ == "__main__":
    unittest.main()
