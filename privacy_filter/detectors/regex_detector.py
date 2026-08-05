"""
Regex Detector Module for FinTech Privacy Filter.

Scans input text using compiled regex pattern definitions from regex_patterns.py,
validates matches (e.g., Luhn checksum for cards), and returns standardized Entity objects.
"""

from dataclasses import asdict, dataclass, field
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
    contributing_sources: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.contributing_sources and self.category:
            self.contributing_sources = [self.category]

    def to_dict(self) -> Dict[str, Any]:
        """Returns entity in standard dictionary format as specified in schema."""
        return {
            "type": self.type,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "category": self.category,
            "contributing_sources": self.contributing_sources,
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
    def is_verhoeff_valid(number_str: str) -> bool:
        """Validates Aadhaar numbers using Verhoeff checksum algorithm."""
        d = (
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
            (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
            (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
            (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
            (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
            (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
            (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
            (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
            (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        )
        p = (
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
            (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
            (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
            (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
            (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
            (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
            (7, 0, 4, 6, 9, 1, 3, 2, 5, 8)
        )
        c = 0
        try:
            for i, digit in enumerate(reversed(number_str)):
                c = d[c][p[i % 8][int(digit)]]
            return c == 0
        except (ValueError, IndexError):
            return False

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
                elif entity_type == EntityType.AADHAAR:
                    cleaned_aadhaar = "".join(c for c in matched_text if c.isdigit())
                    if not self.is_verhoeff_valid(cleaned_aadhaar):
                        confidence = 0.60  # Format matched but failed Verhoeff checksum


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
