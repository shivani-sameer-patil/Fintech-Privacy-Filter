"""
Unit tests for Module 8: merger.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.merger import EntityMerger
from privacy_filter.detectors.regex_detector import Entity


class TestEntityMerger(unittest.TestCase):

    def setUp(self):
        self.merger = EntityMerger()

    def test_empty_input(self):
        self.assertEqual(self.merger.merge([], []), [])

    def test_exact_deduplication(self):
        e1 = Entity(type="PAN", text="ABCDE1234F", start=10, end=20, confidence=0.8)
        e2 = Entity(type="PAN", text="ABCDE1234F", start=10, end=20, confidence=1.0)

        res = self.merger.merge([e1], [e2])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].confidence, 1.0)

    def test_overlap_card_vs_cvv(self):
        card = Entity(type="CARD", text="4111 1111 1111 1111", start=10, end=29, confidence=1.0)
        cvv = Entity(type="CVV", text="4111", start=10, end=14, confidence=1.0)

        res = self.merger.merge([cvv], [card])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].type, "CARD")
        self.assertEqual(res[0].text, "4111 1111 1111 1111")

    def test_overlap_swift_vs_person(self):
        swift_false = Entity(type="SWIFT", text="Customer", start=0, end=8, confidence=1.0)
        person = Entity(type="PERSON", text="Customer Shivani", start=0, end=16, confidence=0.9)

        res = self.merger.merge([swift_false], [person])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].type, "PERSON")

    def test_longest_span_resolution(self):
        short_e = Entity(type="ORG", text="HDFC", start=10, end=14, confidence=0.9)
        long_e = Entity(type="ORG", text="HDFC Bank Limited", start=10, end=27, confidence=0.9)

        res = self.merger.merge([short_e], [long_e])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].text, "HDFC Bank Limited")

    def test_sorted_output_order(self):
        e1 = Entity(type="PHONE", text="9876543210", start=100, end=110)
        e2 = Entity(type="EMAIL", text="user@test.com", start=20, end=33)
        e3 = Entity(type="PAN", text="ABCDE1234F", start=50, end=60)

        res = self.merger.merge([e1, e2, e3])
        self.assertEqual([e.start for e in res], [20, 50, 100])


if __name__ == "__main__":
    unittest.main()
