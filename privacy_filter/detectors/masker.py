"""
Text Masker Module for FinTech Privacy Filter.

Replaces detected sensitive entities with semantic placeholders (e.g. [EMAIL], [PAN], [BANK_ACCOUNT]).
Processes replacements strictly from the END of the document backwards to preserve character offsets.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from privacy_filter.detectors.regex_detector import Entity

# Default semantic placeholder mappings
DEFAULT_TAG_MAPPING: Dict[str, str] = {
    "EMAIL": "[EMAIL]",
    "PAN": "[PAN]",
    "PHONE": "[PHONE_NUMBER]",
    "AADHAAR": "[AADHAAR]",
    "ACCOUNT_NUMBER": "[BANK_ACCOUNT]",
    "BANK_ACCOUNT": "[BANK_ACCOUNT]",
    "LOAN_ACCOUNT": "[LOAN_ACCOUNT]",
    "CARD": "[CARD]",
    "IFSC": "[IFSC]",
    "MICR": "[MICR]",
    "CVV": "[CVV]",
    "UPI": "[UPI]",
    "GST": "[GST]",
    "CIN": "[CIN]",
    "POLICY_NUMBER": "[POLICY_NUMBER]",
    "CHEQUE_NUMBER": "[CHEQUE_NUMBER]",
    "CRYPTO_WALLET": "[CRYPTO_WALLET]",
    "IP_ADDRESS": "[IP_ADDRESS]",
    "MAC_ADDRESS": "[MAC_ADDRESS]",
    "DEVICE_ID": "[DEVICE_ID]",
    "USERNAME": "[USERNAME]",
    "PASSWORD": "[PASSWORD]",
    "OTP": "[OTP]",
    "MPIN": "[MPIN]",
    "TRANSACTION_PIN": "[TRANSACTION_PIN]",
    "PERSON": "[PERSON]",
    "DATE": "[DATE]",
    "AMOUNT": "[AMOUNT]",
    "PASSPORT": "[PASSPORT]",
    "VOTER_ID": "[VOTER_ID]",
    "DRIVING_LICENSE": "[DRIVING_LICENSE]",
    "UNKNOWN_NUMERIC_ID": "[SENSITIVE_ID]",
}


@dataclass
class MaskResult:
    """Structure holding text masking results.

    Attributes:
        masked_text: Final sanitized string with entities replaced by semantic placeholders.
        entities_masked: Total count of masked entity spans.
        entity_counts: Dictionary mapping entity types to count of masked occurrences.
    """
    masked_text: str
    entities_masked: int
    entity_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Returns masking result as standard dictionary."""
        return {
            "masked_text": self.masked_text,
            "entities_masked": self.entities_masked,
            "entity_counts": self.entity_counts,
        }


class Masker:
    """High-performance text masker replacing sensitive entities with semantic placeholders."""

    def __init__(self, tag_mapping: Optional[Dict[str, str]] = None) -> None:
        """Initialize Masker.

        Args:
            tag_mapping: Custom dictionary mapping entity types to replacement tag strings.
        """
        self.tag_mapping = tag_mapping or DEFAULT_TAG_MAPPING

    def get_tag(self, entity_type: str) -> str:
        """Retrieves semantic tag for an entity type or generates generic placeholder."""
        return self.tag_mapping.get(entity_type, f"[{entity_type}]")

    def mask(self, text: str, entities: List[Entity]) -> MaskResult:
        """Replaces detected entities in text with semantic placeholders.

        Process:
        1. Filters valid entity spans.
        2. Sorts entities in reverse order of start offset (from end of document to start).
        3. Replaces spans from right to left to prevent offset shifting.

        Args:
            text: Original document string.
            entities: List of non-overlapping Entity objects.

        Returns:
            MaskResult object containing masked text and masking metrics.
        """
        if not text or not entities:
            return MaskResult(masked_text=text or "", entities_masked=0, entity_counts={})

        # Filter entities with valid character spans
        valid_entities = [
            e for e in entities if 0 <= e.start < e.end <= len(text)
        ]

        # Sort entities in reverse order by start position (end-of-document backwards)
        sorted_entities = sorted(valid_entities, key=lambda e: e.start, reverse=True)

        masked_chars = list(text)
        entity_counts: Dict[str, int] = {}

        for entity in sorted_entities:
            tag = self.get_tag(entity.type)
            start, end = entity.start, entity.end

            # Replace character slice with placeholder string
            masked_chars[start:end] = list(tag)
            entity_counts[entity.type] = entity_counts.get(entity.type, 0) + 1

        final_masked_text = "".join(masked_chars)

        return MaskResult(
            masked_text=final_masked_text,
            entities_masked=len(valid_entities),
            entity_counts=entity_counts,
        )
