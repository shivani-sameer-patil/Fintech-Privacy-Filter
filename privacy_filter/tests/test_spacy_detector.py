"""
Unit tests for Module 4: spacy_detector.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.spacy_detector import (
    SPACY_TARGET_ENTITIES,
    SPACY_TYPE_MAP,
    SpacyDetector,
)


class TestSpacyDetector(unittest.TestCase):

    def setUp(self):
        self.detector = SpacyDetector()

    def test_empty_input(self):
        entities = self.detector.detect("")
        self.assertEqual(entities, [])

    def test_target_entities_set(self):
        self.assertIn("PERSON", SPACY_TARGET_ENTITIES)
        self.assertIn("DATE", SPACY_TARGET_ENTITIES)

    def test_type_mapping(self):
        self.assertEqual(SPACY_TYPE_MAP["PERSON"], "PERSON")
        self.assertEqual(SPACY_TYPE_MAP["DATE"], "DATE")

    def test_graceful_fallback(self):
        detector = SpacyDetector()
        detector._nlp = None
        detector._initialized = False

        self.assertFalse(detector.is_available)
        results = detector.detect("Shivani Patil works at HDFC Bank in Mumbai on 21st July 2026.")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
