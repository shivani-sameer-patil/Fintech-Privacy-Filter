"""
Presidio Detector Module for FinTech Privacy Filter.

Integrates Microsoft Presidio AnalyzerEngine to perform NLP entity detection
and maps Presidio recognition results into standard Entity objects.
"""

import logging
from typing import Dict, List, Optional

from privacy_filter.detectors.regex_detector import Entity

logger = logging.getLogger(__name__)

# Standard mapping from Presidio Entity types to FinTech Privacy Filter Entity types
PRESIDIO_TYPE_MAP: Dict[str, str] = {
    "PERSON": "PERSON",
    "EMAIL_ADDRESS": "EMAIL",
    "PHONE_NUMBER": "PHONE",
    "CREDIT_CARD": "CARD",
    "IP_ADDRESS": "IP_ADDRESS",
    "DATE_TIME": "DATE",
    "IN_PAN": "PAN",
    "IN_AADHAAR": "AADHAAR",
    "IN_PASSPORT": "PASSPORT",
    "IN_VOTER_ID": "VOTER_ID",
    "URL": "URL",
}


class PresidioDetector:
    """Detector engine leveraging Microsoft Presidio AnalyzerEngine."""

    def __init__(
        self,
        type_mapping: Optional[Dict[str, str]] = None,
        score_threshold: float = 0.4,
    ) -> None:
        """Initialize PresidioDetector.

        Args:
            type_mapping: Custom dictionary mapping Presidio entities to pipeline entity types.
            score_threshold: Minimum confidence score threshold (0.0 - 1.0).
        """
        self.type_mapping = type_mapping or PRESIDIO_TYPE_MAP
        self.score_threshold = score_threshold
        self._analyzer = None
        self._initialized = False

        self._initialize_engine()

    def _initialize_engine(self) -> None:
        """Initializes Presidio AnalyzerEngine lazily and safely."""
        try:
            from presidio_analyzer import AnalyzerEngine
            self._analyzer = AnalyzerEngine()
            self._initialized = True
            logger.info("Presidio AnalyzerEngine initialized successfully.")
        except Exception as err:
            logger.warning(
                "Failed to initialize Presidio AnalyzerEngine (%s). Detector will run in fallback mode.",
                err,
            )
            self._initialized = False

    @property
    def is_available(self) -> bool:
        """Returns True if Presidio engine is loaded and operational."""
        return self._initialized and self._analyzer is not None

    def detect(self, text: str, language: str = "en") -> List[Entity]:
        """Scans input text using Presidio AnalyzerEngine.

        Args:
            text: Source string to analyze.
            language: Two-letter ISO language code (default: 'en').

        Returns:
            List of standardized Entity objects.
        """
        if not text or not self.is_available:
            return []

        try:
            results = self._analyzer.analyze(
                text=text,
                language=language,
                score_threshold=self.score_threshold,
            )

            entities: List[Entity] = []
            for res in results:
                if res.entity_type not in self.type_mapping:
                    continue
                mapped_type = self.type_mapping[res.entity_type]
                matched_text = text[res.start : res.end]

                entity = Entity(
                    type=mapped_type,
                    text=matched_text,
                    start=res.start,
                    end=res.end,
                    confidence=float(res.score),
                    category="PRESIDIO_NLP",
                )
                entities.append(entity)

            # Sort by start offset
            entities.sort(key=lambda e: (e.start, -(e.end - e.start)))
            return entities

        except Exception as err:
            logger.error("Error during Presidio detection scanning: %s", err)
            return []
