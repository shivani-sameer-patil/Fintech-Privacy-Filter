"""
Unit tests for Module 6: indic_normalizer.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.indic_normalizer import IndicNormalizer


class TestIndicNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = IndicNormalizer()

    def test_empty_and_normal_ascii_text(self):
        self.assertEqual(self.normalizer.normalize_text(""), "")
        self.assertEqual(self.normalizer.normalize_text("Account 1234"), "Account 1234")
        self.assertFalse(self.normalizer.has_indic_numerals("Account 1234"))

    def test_devanagari_numeral_normalization(self):
        input_text = "खाता: १२३४५६७८९०"
        expected = "खाता: 1234567890"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_kannada_numeral_normalization(self):
        input_text = "ಖಾತೆ: ೧೨೩೪೫೬೭೮೯೦"
        expected = "ಖಾತೆ: 1234567890"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_bengali_numeral_normalization(self):
        input_text = "অ্যাকাউন্ট: ১২৩৪৫৬৭৮৯০"
        expected = "অ্যাকাউন্ট: 1234567890"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_tamil_numeral_normalization(self):
        input_text = "கணக்கு: ௦௧௨௩௪௫௬௭௮௯"
        expected = "கணக்கு: 0123456789"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_telugu_numeral_normalization(self):
        input_text = "ఖాతా: ౦౧౨౩౪౫౬౭౮౯"
        expected = "ఖాతా: 0123456789"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_malayalam_numeral_normalization(self):
        input_text = "അക്കൗണ്ട്: ൦൧൨൩൪൫൬൭൮൯"
        expected = "അക്കൗണ്ട്: 0123456789"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_gujarati_numeral_normalization(self):
        input_text = "ખાતું: ૦૧૨૩૪૫૬૭૮૯"
        expected = "ખાતું: 0123456789"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_gurmukhi_numeral_normalization(self):
        input_text = "ਖਾਤਾ: ੦੧੨੩੪੫੬੭੮੯"
        expected = "ਖਾਤਾ: 0123456789"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_odia_numeral_normalization(self):
        input_text = "ଖାତା: ୦୧୨୩୪୫୬୭୮୯"
        expected = "ଖାତା: 0123456789"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)

    def test_perso_arabic_numeral_normalization(self):
        input_text = "کھاتہ: ۰۱۲۳۴۵۶۷۸۹"
        expected = "کھاتہ: 0123456789"
        self.assertTrue(self.normalizer.has_indic_numerals(input_text))
        self.assertEqual(self.normalizer.normalize_text(input_text), expected)


if __name__ == "__main__":
    unittest.main()
