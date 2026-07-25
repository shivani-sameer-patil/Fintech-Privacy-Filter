"""
Regex Detector Module for FinTech Privacy Filter.

Scans input text using compiled regex pattern definitions from regex_patterns.py,
validates matches (e.g., Luhn checksum for cards), and returns standardized Entity objects.
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Set

from privacy_filter.detectors.regex_patterns import (
    EntityCategory,
    EntityType,
    RegexPatternRegistry,
)


@dataclass
class Entity:
    """Standardized entity representation across all detector engines.

    Attributes:
        type: Entity type name (e.g. 'PAN', 'EMAIL', 'BANK_ACCOUNT').
        text: Matched string segment from the source text.
        start: 0-indexed start character position (inclusive).
        end: 0-indexed end character position (exclusive).
        confidence: Confidence score floating point value between 0.0 and 1.0.
        category: Functional entity category name.
    """
    type: str
    text: str
    start: int
    end: int
    confidence: float = 1.0
    category: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Returns entity in standard dictionary format as specified in schema."""
        return {
            "type": self.type,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
        }


class RegexDetector:
    """High-performance detector using rule-based regular expressions."""

    def __init__(
        self,
        enabled_categories: Optional[Set[EntityCategory]] = None,
        enabled_types: Optional[Set[EntityType]] = None,
        min_confidence: float = 0.5,
    ) -> None:
        """Initialize RegexDetector with optional filtering configurations.

        Args:
            enabled_categories: Optional subset of EntityCategory to scan.
            enabled_types: Optional subset of EntityType to scan.
            min_confidence: Minimum confidence threshold for detected entities.
        """
        self.enabled_categories = enabled_categories
        self.enabled_types = enabled_types
        self.min_confidence = min_confidence

    @staticmethod
    def is_luhn_valid(card_number_str: str) -> bool:
        """Validates credit/debit card numbers using Luhn checksum algorithm."""
        digits = [int(ch) for ch in card_number_str if ch.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        checksum = 0
        reverse_digits = digits[::-1]
        for idx, digit in enumerate(reverse_digits):
            if idx % 2 == 1:
                doubled = digit * 2
                checksum += doubled - 9 if doubled > 9 else doubled
            else:
                checksum += digit
        return checksum % 10 == 0

    @staticmethod
    def is_swift_valid(swift_code: str) -> bool:
        """Validates SWIFT/BIC codes using country code validation (characters 5-6)."""
        if len(swift_code) not in (8, 11):
            return False
        country_code = swift_code[4:6].upper()
        valid_countries = {
            "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ",
            "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS",
            "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN",
            "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE",
            "EG", "EH", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF",
            "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM",
            "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM",
            "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC",
            "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK",
            "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA",
            "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG",
            "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW",
            "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS",
            "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO",
            "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI",
            "VN", "VU", "WF", "WS", "YE", "YT", "ZA", "ZM", "ZW"
        }
        return country_code in valid_countries

    def detect(self, text: str) -> List[Entity]:
        """Scans input text and returns detected sensitive entities.

        Args:
            text: Raw input string to scan.

        Returns:
            List of detected Entity objects sorted by start position.
        """
        if not text:
            return []

        all_patterns = RegexPatternRegistry.get_all_patterns()
        entities: List[Entity] = []

        for entity_type, pattern_def in all_patterns.items():
            # Category filter check
            if (
                self.enabled_categories
                and pattern_def.category not in self.enabled_categories
            ):
                continue

            # Entity type filter check
            if self.enabled_types and entity_type not in self.enabled_types:
                continue

            compiled_regex = pattern_def.compiled_regex

            for match in compiled_regex.finditer(text):
                # If the regex has capturing groups, use the first non-None group's span and text
                # to avoid masking label prefixes (e.g. 'Password: ')
                group_idx = 0
                if match.groups():
                    for i, val in enumerate(match.groups(), start=1):
                        if val is not None:
                            group_idx = i
                            break

                if group_idx > 0:
                    matched_text = match.group(group_idx)
                    start, end = match.span(group_idx)
                else:
                    matched_text = match.group(0)
                    start, end = match.span()

                confidence = 1.0

                # Checksum validation & confidence scoring adjustments
                if entity_type == EntityType.CARD:
                    cleaned_card = "".join(c for c in matched_text if c.isdigit())
                    if not self.is_luhn_valid(cleaned_card):
                        confidence = 0.70  # Format matched but failed Luhn checksum

                if entity_type == EntityType.SWIFT:
                    if not self.is_swift_valid(matched_text):
                        continue

                if confidence >= self.min_confidence:
                    entity = Entity(
                        type=entity_type.value,
                        text=matched_text,
                        start=start,
                        end=end,
                        confidence=confidence,
                        category=pattern_def.category.name,
                    )
                    entities.append(entity)

        # Sort entities primarily by start index, secondarily by longest span
        entities.sort(key=lambda e: (e.start, -(e.end - e.start)))
        return entities
