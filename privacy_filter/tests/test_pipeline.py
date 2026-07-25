"""
End-to-End Integration Unit Tests for Module 10: pipeline.py
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.config import PipelineConfig
from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline, PipelineOutput


class TestFinTechPrivacyPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = FinTechPrivacyPipeline()

    def test_empty_input(self):
        output = self.pipeline.process("")
        self.assertIsInstance(output, PipelineOutput)
        self.assertEqual(output.masked_text, "")
        self.assertEqual(output.entities_masked_count, 0)

    def test_end_to_end_financial_email(self):
        text = (
            "Dear Customer Shivani Patil,\n"
            "Your PAN ABCDE1234F and Aadhaar 2345 6789 0123 are verified.\n"
            "Bank Account Number: 123456789012 with IFSC SBIN0001234.\n"
            "Card used: 4111 1111 1111 1111. Contact us at support@fintech.co.in or +91 9876543210.\n"
            "GSTIN: 27ABCDE1234F1Z5, CIN: U72200MH2020PTC123456."
        )

        output = self.pipeline.process(text)
        self.assertIsInstance(output, PipelineOutput)
        self.assertGreater(output.entities_masked_count, 0)
        self.assertNotIn("ABCDE1234F", output.masked_text)
        self.assertNotIn("shivani@gmail.com", output.masked_text)
        self.assertNotIn("4111 1111 1111 1111", output.masked_text)
        self.assertIn("[PAN]", output.masked_text)
        self.assertIn("[AADHAAR]", output.masked_text)
        self.assertIn("[BANK_ACCOUNT]", output.masked_text)
        self.assertIn("[CARD]", output.masked_text)
        self.assertIn("[EMAIL]", output.masked_text)
        self.assertIn("[GST]", output.masked_text)
        self.assertIn("[CIN]", output.masked_text)

    def test_indic_numeral_end_to_end_pipeline(self):
        # Hindi document with Devanagari numerals
        text = "नमस्ते, बैंक खाता संख्या: १२३४५६७८९०१२ और आधार: २३ND45 6789 0123"
        hindi_text = "नमस्ते, बैंक खाता संख्या: १२३४५६७८९०१२"

        output = self.pipeline.process(hindi_text)
        self.assertIn(output.language.language_code, {"hi", "mr"})
        self.assertEqual(output.normalized_text, "नमस्ते, बैंक खाता संख्या: 123456789012")
        self.assertIn("[BANK_ACCOUNT]", output.masked_text)
        self.assertNotIn("123456789012", output.masked_text)

    def test_pipeline_to_dict_schema(self):
        text = "PAN ABCDE1234F"
        output = self.pipeline.process(text)
        res_dict = output.to_dict()

        self.assertIn("original_text", res_dict)
        self.assertIn("normalized_text", res_dict)
        self.assertIn("masked_text", res_dict)
        self.assertIn("language", res_dict)
        self.assertIn("detected_entities", res_dict)
        self.assertIn("processing_time_ms", res_dict)


if __name__ == "__main__":
    unittest.main()
