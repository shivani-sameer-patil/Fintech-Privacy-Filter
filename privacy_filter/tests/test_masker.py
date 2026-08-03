"""
Unit tests for Module 9: masker.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.masker import Masker, MaskResult
from privacy_filter.detectors.regex_detector import Entity


class TestMasker(unittest.TestCase):

    def setUp(self):
        self.masker = Masker()

    def test_empty_input(self):
        res = self.masker.mask("", [])
        self.assertEqual(res.masked_text, "")
        self.assertEqual(res.entities_masked, 0)

    def test_single_entity_replacement(self):
        text = "Customer PAN is ABCDE1234F for verification."
        entity = Entity(type="PAN", text="ABCDE1234F", start=16, end=26)

        res = self.masker.mask(text, [entity])
        self.assertEqual(res.masked_text, "Customer PAN is [PAN] for verification.")
        self.assertEqual(res.entities_masked, 1)
        self.assertEqual(res.entity_counts["PAN"], 1)

    def test_multiple_entity_replacements(self):
        text = "Contact Shivani Patil at shivani@gmail.com or +91 9876543210."
        entities = [
            Entity(type="PERSON", text="Shivani Patil", start=8, end=21),
            Entity(type="EMAIL", text="shivani@gmail.com", start=25, end=42),
            Entity(type="PHONE", text="+91 9876543210", start=46, end=60),
        ]

        res = self.masker.mask(text, entities)
        expected = "Contact Shivani Patil at [EMAIL] or [PHONE_NUMBER]."
        self.assertEqual(res.masked_text, expected)
        self.assertEqual(res.entities_masked, 2)

    def test_right_to_left_offset_preservation(self):
        text = "PAN ABCDE1234F and Aadhaar 2345 6789 0123"
        entities = [
            Entity(type="PAN", text="ABCDE1234F", start=4, end=14),
            Entity(type="AADHAAR", text="2345 6789 0123", start=27, end=41),
        ]

        res = self.masker.mask(text, entities)
        self.assertEqual(res.masked_text, "PAN [PAN] and Aadhaar [AADHAAR]")

    def test_custom_tag_mapping(self):
        custom_masker = Masker(tag_mapping={"PAN": "<PAN_MASKED>"})
        text = "PAN is ABCDE1234F."
        entity = Entity(type="PAN", text="ABCDE1234F", start=7, end=17)

        res = custom_masker.mask(text, [entity])
        self.assertEqual(res.masked_text, "PAN is <PAN_MASKED>.")


if __name__ == "__main__":
    unittest.main()
