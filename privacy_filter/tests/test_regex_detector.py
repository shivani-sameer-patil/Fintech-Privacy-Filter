"""
Unit tests for Module 2: regex_detector.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.regex_detector import Entity, RegexDetector
from privacy_filter.detectors.regex_patterns import EntityCategory, EntityType


class TestRegexDetector(unittest.TestCase):

    def setUp(self):
        self.detector = RegexDetector()

    def test_empty_input(self):
        entities = self.detector.detect("")
        self.assertEqual(entities, [])

    def test_entity_to_dict_format(self):
        entity = Entity(
            type="PAN",
            text="ABCDE1234F",
            start=10,
            end=20,
            confidence=1.0,
            category="PERSONAL",
        )
        expected_dict = {
            "type": "PAN",
            "text": "ABCDE1234F",
            "start": 10,
            "end": 20,
            "confidence": 1.0,
        }
        self.assertEqual(entity.to_dict(), expected_dict)

    def test_pan_detection_offsets(self):
        text = "Customer PAN is ABCDE1234F for verification."
        entities = self.detector.detect(text)
        pan_entities = [e for e in entities if e.type == "PAN"]
        self.assertEqual(len(pan_entities), 1)
        e = pan_entities[0]
        self.assertEqual(e.type, "PAN")
        self.assertEqual(e.text, "ABCDE1234F")
        self.assertEqual(e.start, 16)
        self.assertEqual(e.end, 26)
        self.assertEqual(text[e.start:e.end], "ABCDE1234F")

    def test_luhn_checksum_validation(self):
        # 4111 1111 1111 1111 -> Valid Luhn checksum
        # 4111 1111 1111 1112 -> Invalid Luhn checksum
        valid_card_text = "Card: 4111 1111 1111 1111"
        invalid_card_text = "Card: 4111 1111 1111 1112"

        valid_entities = self.detector.detect(valid_card_text)
        valid_card = [e for e in valid_entities if e.type == "CARD"][0]
        self.assertEqual(valid_card.confidence, 1.0)

        invalid_entities = self.detector.detect(invalid_card_text)
        invalid_card = [e for e in invalid_entities if e.type == "CARD"][0]
        self.assertEqual(invalid_card.confidence, 0.70)

    def test_category_filtering(self):
        detector = RegexDetector(enabled_categories={EntityCategory.PERSONAL})
        text = "PAN ABCDE1234F and GSTIN 27ABCDE1234F1Z5"
        entities = detector.detect(text)
        types = [e.type for e in entities]
        self.assertIn("PAN", types)
        self.assertNotIn("GST", types)

    def test_type_filtering(self):
        detector = RegexDetector(enabled_types={EntityType.EMAIL})
        text = "Email user@example.com and PAN ABCDE1234F"
        entities = detector.detect(text)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0].type, "EMAIL")


if __name__ == "__main__":
    unittest.main()
