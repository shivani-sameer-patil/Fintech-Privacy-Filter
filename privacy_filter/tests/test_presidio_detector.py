"""
Unit tests for Module 3: presidio_detector.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.presidio_detector import (
    PRESIDIO_TYPE_MAP,
    PresidioDetector,
)
from privacy_filter.detectors.regex_detector import Entity


class TestPresidioDetector(unittest.TestCase):

    def setUp(self):
        self.detector = PresidioDetector()

    def test_empty_input(self):
        entities = self.detector.detect("")
        self.assertEqual(entities, [])

    def test_type_mapping_dictionary(self):
        self.assertEqual(PRESIDIO_TYPE_MAP["EMAIL_ADDRESS"], "EMAIL")
        self.assertEqual(PRESIDIO_TYPE_MAP["PHONE_NUMBER"], "PHONE")
        self.assertEqual(PRESIDIO_TYPE_MAP["CREDIT_CARD"], "CARD")
        self.assertEqual(PRESIDIO_TYPE_MAP["PERSON"], "PERSON")

    def test_custom_type_mapping(self):
        custom_map = {"EMAIL_ADDRESS": "CUSTOM_EMAIL"}
        detector = PresidioDetector(type_mapping=custom_map)
        self.assertEqual(detector.type_mapping["EMAIL_ADDRESS"], "CUSTOM_EMAIL")

    def test_graceful_fallback(self):
        # Force analyzer to None to test fallback
        detector = PresidioDetector()
        detector._analyzer = None
        detector._initialized = False

        self.assertFalse(detector.is_available)
        results = detector.detect("John Doe email is john@example.com")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
