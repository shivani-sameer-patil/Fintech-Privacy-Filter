"""
Entity Merger Module for FinTech Privacy Filter.

Merges detection candidate entities from Regex, Presidio, spaCy, and Context Classifier engines,
eliminates duplicates, resolves span overlaps based on confidence and span length, and returns sorted entities.
"""

from typing import List, Set

from privacy_filter.detectors.regex_detector import Entity

# Entity type priority ranking (higher value = higher precedence when resolving overlaps)
TYPE_PRIORITY = {
    "CARD": 100,
    "PASSWORD": 95,
    "USERNAME": 95,
    "PAN": 95,
    "GST": 95,
    "CIN": 95,
    "AADHAAR": 90,
    "PHONE": 90,
    "EMAIL": 90,
    "UPI": 90,
    "DEVICE_ID": 90,
    "IP_ADDRESS": 90,
    "MAC_ADDRESS": 90,
    "CRYPTO_WALLET": 90,
    "AMOUNT": 85,
    "IFSC": 85,
    "MICR": 85,
    "PASSPORT": 85,
    "VOTER_ID": 85,
    "DRIVING_LICENSE": 85,
    "LOAN_ACCOUNT": 80,
    "POLICY_NUMBER": 80,
    "OTP": 80,
    "MPIN": 80,
    "TRANSACTION_PIN": 80,
    "ACCOUNT_NUMBER": 75,
    "PERSON": 70,
    "ORG": 70,
    "DATE": 70,
    "CHEQUE_NUMBER": 55,
    "SWIFT": 30,
    "CVV": 25,
    "UNKNOWN_NUMERIC_ID": 10,
}


class EntityMerger:
    """Consolidates and resolves overlapping entity candidate spans across detector engines."""

    def __init__(self, type_priority: dict[str, int] = None) -> None:
        """Initialize EntityMerger.

        Args:
            type_priority: Custom dictionary assigning precedence rank integer to entity types.
        """
        self.type_priority = type_priority or TYPE_PRIORITY

    def _get_priority(self, entity: Entity) -> int:
        """Returns integer precedence rank for an entity type."""
        return self.type_priority.get(entity.type, 50)

    @staticmethod
    def _is_overlapping(e1: Entity, e2: Entity) -> bool:
        """Checks if two entity character spans overlap."""
        return max(e1.start, e2.start) < min(e1.end, e2.end)

    def _should_keep_first(self, e1: Entity, e2: Entity) -> bool:
        """Determines if entity e1 should be preserved over entity e2 when they overlap.

        Decision criteria (in order of evaluation):
        1. Higher Type Priority (e.g. CARD over CVV or SWIFT)
        2. Higher Confidence score
        3. Longest Character Span length (end - start)
        """
        p1 = self._get_priority(e1)
        p2 = self._get_priority(e2)

        if p1 != p2:
            return p1 > p2

        if abs(e1.confidence - e2.confidence) > 1e-4:
            return e1.confidence > e2.confidence

        len1 = e1.end - e1.start
        len2 = e2.end - e2.start
        return len1 >= len2

    def merge(self, *entity_lists: List[Entity]) -> List[Entity]:
        """Merges multiple lists of Entity objects into a single non-overlapping sorted list.

        Args:
            *entity_lists: One or more lists of Entity candidates.

        Returns:
            Deduplicated, non-overlapping List of Entity objects sorted by start offset.
        """
        all_candidates: List[Entity] = []
        for elist in entity_lists:
            if elist:
                all_candidates.extend(elist)

        if not all_candidates:
            return []

        # 1. Exact Deduplication
        unique_map: dict[tuple[int, int, str], Entity] = {}
        for entity in all_candidates:
            key = (entity.start, entity.end, entity.type)
            if key not in unique_map or entity.confidence > unique_map[key].confidence:
                unique_map[key] = entity

        candidates = list(unique_map.values())

        # Sort candidates by start position ascending, span length descending, priority descending
        candidates.sort(
            key=lambda e: (
                e.start,
                -(e.end - e.start),
                -self._get_priority(e),
                -e.confidence,
            )
        )

        # 2. Overlap Resolution greedy pass
        merged_entities: List[Entity] = []

        for candidate in candidates:
            overlap_found = False

            for idx, existing in enumerate(merged_entities):
                if self._is_overlapping(candidate, existing):
                    overlap_found = True
                    # Check if candidate replaces existing entity
                    if not self._should_keep_first(existing, candidate):
                        merged_entities[idx] = candidate
                    break

            if not overlap_found:
                merged_entities.append(candidate)

        # Re-sort final non-overlapping entities by start index
        merged_entities.sort(key=lambda e: (e.start, e.end))
        return merged_entities
