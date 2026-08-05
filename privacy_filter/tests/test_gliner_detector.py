"""
Unit tests for Module: gliner_detector.py
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.gliner_detector import GLINER_TYPE_MAP, GlinerDetector
from privacy_filter.detectors.regex_detector import Entity


class TestGlinerDetector(unittest.TestCase):

    @patch("gliner.GLiNER")
    def test_mock_detection(self, mock_gliner_cls):
        # Setup mock model behavior
        mock_model = MagicMock()
        mock_gliner_cls.from_pretrained.return_value = mock_model
        mock_model.predict_entities.return_value = [
            {"start": 13, "end": 26, "text": "Shivani Patil", "label": "person", "score": 0.98},
            {"start": 36, "end": 45, "text": "HDFC Bank", "label": "organization", "score": 0.95},
        ]

        detector = GlinerDetector(model_name="urchade/gliner_large-v2.1", threshold=0.5)
        self.assertTrue(detector.is_available)

        text = "Hello, I am Shivani Patil working at HDFC Bank."
        entities = detector.detect(text)

        self.assertEqual(len(entities), 2)

        # First entity checking
        self.assertEqual(entities[0].type, "PERSON")
        self.assertEqual(entities[0].text, "Shivani Patil")
        self.assertEqual(entities[0].start, 13)
        self.assertEqual(entities[0].end, 26)
        self.assertAlmostEqual(entities[0].confidence, 0.98)
        self.assertEqual(entities[0].category, "GLINER_NER")

        # Second entity checking
        self.assertEqual(entities[1].type, "ORG")
        self.assertEqual(entities[1].text, "HDFC Bank")
        self.assertEqual(entities[1].start, 36)
        self.assertEqual(entities[1].end, 45)
        self.assertAlmostEqual(entities[1].confidence, 0.95)
        self.assertEqual(entities[1].category, "GLINER_NER")

    def test_empty_input(self):
        detector = GlinerDetector()
        self.assertEqual(detector.detect(""), [])

    def test_type_mapping(self):
        self.assertEqual(GLINER_TYPE_MAP["person"], "PERSON")
        self.assertEqual(GLINER_TYPE_MAP["organization"], "ORG")
        self.assertEqual(GLINER_TYPE_MAP["credit card"], "CARD")

    def test_graceful_fallback(self):
        detector = GlinerDetector()
        detector._model = None
        detector._initialized = False

        self.assertFalse(detector.is_available)
        results = detector.detect("Shivani Patil works at HDFC Bank.")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
