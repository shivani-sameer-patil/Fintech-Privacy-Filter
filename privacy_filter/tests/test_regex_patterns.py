"""
Unit tests for Module 1: regex_patterns.py using Python standard library unittest.
"""

import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from privacy_filter.detectors.regex_patterns import (
    EntityCategory,
    EntityType,
    RegexPatternRegistry,
    PatternDefinition,
)


class TestRegexPatterns(unittest.TestCase):

    def test_all_entity_types_registered(self):
        all_patterns = RegexPatternRegistry.get_all_patterns()
        for entity_type in EntityType:
            with self.subTest(entity_type=entity_type):
                self.assertIn(entity_type, all_patterns)
                pattern_def = all_patterns[entity_type]
                self.assertIsInstance(pattern_def, PatternDefinition)
                self.assertEqual(pattern_def.entity_type, entity_type)
                self.assertIsNotNone(pattern_def.compiled_regex)
                self.assertTrue(pattern_def.description)
                self.assertGreater(len(pattern_def.examples), 0)

    def test_category_filtering(self):
        personal_patterns = RegexPatternRegistry.get_patterns_by_category(EntityCategory.PERSONAL)
        self.assertEqual(len(personal_patterns), 8)
        types_in_personal = {p.entity_type for p in personal_patterns}
        self.assertIn(EntityType.EMAIL, types_in_personal)
        self.assertIn(EntityType.PAN, types_in_personal)
        self.assertIn(EntityType.AADHAAR, types_in_personal)
        self.assertIn(EntityType.DATE, types_in_personal)

    def test_registered_examples_match(self):
        for entity_type in EntityType:
            pattern_def = RegexPatternRegistry.get_pattern(entity_type)
            self.assertIsNotNone(pattern_def)
            for example in pattern_def.examples:
                with self.subTest(entity_type=entity_type, example=example):
                    match = pattern_def.compiled_regex.search(example)
                    self.assertIsNotNone(
                        match, f"Example '{example}' failed to match regex for {entity_type.name}"
                    )

    def test_email_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.EMAIL).compiled_regex
        self.assertTrue(p.search("Contact user@example.com for details"))
        self.assertTrue(p.search("Email: test.user+label@fintech.co.in"))
        self.assertFalse(p.search("NotAnEmail@"))
        self.assertFalse(p.search("user@domain"))

    def test_phone_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.PHONE).compiled_regex
        self.assertTrue(p.search("Call +91 9876543210 immediately"))
        self.assertTrue(p.search("Phone: 98765 43210"))
        self.assertFalse(p.search("Phone: 98765-43210"))
        self.assertTrue(p.search("Mobile 09123456789"))
        self.assertFalse(p.search("Number 1234567890"))

    def test_pan_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.PAN).compiled_regex
        self.assertTrue(p.search("PAN is ABCDE1234F"))
        self.assertTrue(p.search("Company PAN: XYZPC9999Z"))
        self.assertFalse(p.search("ABCZE1234F"))
        self.assertFalse(p.search("ABCDE12345F"))

    def test_aadhaar_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.AADHAAR).compiled_regex
        self.assertTrue(p.search("Aadhaar: 2345 6789 0123"))
        self.assertTrue(p.search("Aadhaar: 9876-5432-1098"))
        self.assertTrue(p.search("Aadhaar: 543210987654"))
        self.assertTrue(p.search("123456789012"))

    def test_passport_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.PASSPORT).compiled_regex
        self.assertTrue(p.search("Passport No: A1234567"))
        self.assertTrue(p.search("Passport Z9876543"))
        self.assertFalse(p.search("Passport A0234567"))

    def test_ifsc_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.IFSC).compiled_regex
        self.assertTrue(p.search("IFSC: SBIN0001234"))
        self.assertTrue(p.search("Code HDFC0000240"))
        self.assertFalse(p.search("SBIN1001234"))

    def test_card_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.CARD).compiled_regex
        self.assertTrue(p.search("Visa 4111 1111 1111 1111"))
        self.assertTrue(p.search("MC 5500-0000-0000-0004"))

    def test_gst_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.GST).compiled_regex
        self.assertTrue(p.search("GSTIN: 27ABCDE1234F1Z5"))
        self.assertFalse(p.search("27ABCDE1234F1A5"))

    def test_cin_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.CIN).compiled_regex
        self.assertTrue(p.search("CIN: U72200MH2020PTC123456"))
        self.assertTrue(p.search("CIN: L15140GJ1991PLC016139"))

    def test_crypto_wallet_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.CRYPTO_WALLET).compiled_regex
        self.assertTrue(p.search("ETH 0x71C7656EC7ab88b098defB751B7401B5f6d8976F"))
        self.assertTrue(p.search("BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"))
        self.assertTrue(p.search("BTC Segwit 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"))
        self.assertTrue(p.search("BTC Bech32 bc1qvqcf294yd03ycah56xly0n9xfzcd74nn29ydlj"))

    def test_security_patterns(self):
        ip_regex = RegexPatternRegistry.get_pattern(EntityType.IP_ADDRESS).compiled_regex
        self.assertTrue(ip_regex.search("Server IP 192.168.1.1"))

        mac_regex = RegexPatternRegistry.get_pattern(EntityType.MAC_ADDRESS).compiled_regex
        self.assertTrue(mac_regex.search("MAC 00:1A:2B:3C:4D:5E"))

        otp_regex = RegexPatternRegistry.get_pattern(EntityType.OTP).compiled_regex
        self.assertTrue(otp_regex.search("Your OTP: 482910"))

        pwd_regex = RegexPatternRegistry.get_pattern(EntityType.PASSWORD).compiled_regex
        self.assertTrue(pwd_regex.search("password: SecretPass123!"))
        self.assertTrue(pwd_regex.search("पासवर्ड: SecretP@ssw0rd2026!"))
        self.assertTrue(pwd_regex.search("পাসওয়ার্ড: SecretP@ssw0rd2026!"))
        self.assertTrue(pwd_regex.search("പാസ്‌വേഡ്: SecretP@ssw0rd2026!"))

        user_regex = RegexPatternRegistry.get_pattern(EntityType.USERNAME).compiled_regex
        self.assertTrue(user_regex.search("username: shivani_p"))
        self.assertTrue(user_regex.search("उपयोगकर्ता नाम: admin_shivani"))
        self.assertTrue(user_regex.search("ব্যবহারকারীর নাম: admin_shivani"))
        self.assertTrue(user_regex.search("ഉപയോക്തൃനാമം: admin_shivani"))

    def test_amount_regex(self):
        p = RegexPatternRegistry.get_pattern(EntityType.AMOUNT).compiled_regex
        self.assertTrue(p.search("Premium Amount: Rs. 12,500/year"))
        self.assertTrue(p.search("Sanctioned Amount: Rs. 25,00,000.00 per year"))
        self.assertTrue(p.search("Monthly EMI: Rs. 24,500/month"))
        self.assertTrue(p.search("amount can be 23,456/-"))
        self.assertTrue(p.search("45,67,400.00/-"))
        self.assertTrue(p.search("he paid fifteen thousand two hundred thirty six rupees/annum"))


if __name__ == "__main__":
    unittest.main()
