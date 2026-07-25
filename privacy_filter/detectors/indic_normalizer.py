"""
Indic Normalizer Module for FinTech Privacy Filter.

Converts all official Indian numeral systems (Devanagari, Bengali, Kannada, Tamil,
Telugu, Malayalam, Gujarati, Gurmukhi, Odia, Ol Chiki, Meitei Mayek, Perso-Arabic)
into standard ASCII digits (0-9) while leaving non-digit text unchanged.
"""

from typing import Dict

# List of Unicode ranges (start_codepoint, end_codepoint) for official Indian digit systems
INDIC_NUMERAL_RANGES = [
    (0x0966, 0x096F),  # Devanagari (Hindi, Marathi, Konkani, Dogri, Bodo, Maithili, Nepali)
    (0x09E6, 0x09EF),  # Bengali / Assamese
    (0x0A66, 0x0A6F),  # Gurmukhi (Punjabi)
    (0x0AE6, 0x0AEF),  # Gujarati
    (0x0B66, 0x0B6F),  # Odia
    (0x0BE6, 0x0BEF),  # Tamil
    (0x0C66, 0x0C6F),  # Telugu
    (0x0CE6, 0x0CEF),  # Kannada
    (0x0D66, 0x0D6F),  # Malayalam
    (0x1C50, 0x1C59),  # Ol Chiki (Santali)
    (0xABF0, 0xABF9),  # Meitei Mayek (Manipuri)
    (0x0660, 0x0669),  # Arabic-Indic (Urdu / Arabic)
    (0x06F0, 0x06F9),  # Extended Arabic-Indic (Perso-Arabic / Urdu)
]


def _build_indic_digit_map() -> Dict[str, str]:
    """Generates translation mapping dictionary for all Indian numeral systems."""
    digit_map: Dict[str, str] = {}
    for start_cp, end_cp in INDIC_NUMERAL_RANGES:
        for idx, cp in enumerate(range(start_cp, end_cp + 1)):
            digit_map[chr(cp)] = str(idx)
    return digit_map


INDIC_DIGIT_MAP: Dict[str, str] = _build_indic_digit_map()


class IndicNormalizer:
    """High-performance numeral normalizer converting Indic script digits to ASCII."""

    def __init__(self) -> None:
        """Constructs string translation table for zero-overhead C-speed normalization."""
        self._trans_table = str.maketrans(INDIC_DIGIT_MAP)

    def normalize_text(self, text: str) -> str:
        """Normalizes Indic digits in input text to standard ASCII digits ('0'-'9').

        Args:
            text: Input document string containing potential Indic numerals.

        Returns:
            Normalized string with all Indic digits converted to ASCII digits.
        """
        if not text:
            return ""

        return text.translate(self._trans_table)

    def has_indic_numerals(self, text: str) -> bool:
        """Checks if input text contains any non-ASCII Indic numerals."""
        if not text:
            return False
        return any(ch in INDIC_DIGIT_MAP for ch in text)
