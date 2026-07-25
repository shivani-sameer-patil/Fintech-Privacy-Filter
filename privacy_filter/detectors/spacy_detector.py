"""
spaCy Detector Module for FinTech Privacy Filter.

Uses spaCy's Named Entity Recognition (NER) models (en_core_web_lg) to detect
PERSON, ORG, LOC, DATE, and GPE entities and convert them to standard Entity format.
"""

import logging
from typing import Dict, List, Optional, Set

from privacy_filter.detectors.regex_detector import Entity

logger = logging.getLogger(__name__)

# Default target spaCy entity types
SPACY_TARGET_ENTITIES: Set[str] = {"PERSON", "ORG", "LOC", "DATE", "GPE"}

# Standard mapping from spaCy Entity labels to pipeline Entity types
SPACY_TYPE_MAP: Dict[str, str] = {
    "PERSON": "PERSON",
    "ORG": "ORG",
    "LOC": "LOC",
    "DATE": "DATE",
    "GPE": "GPE",
}


class SpacyDetector:
    """Named Entity Recognition detector leveraging spaCy NLP models."""

    def __init__(
        self,
        model_name: str = "en_core_web_lg",
        target_entities: Optional[Set[str]] = None,
        type_mapping: Optional[Dict[str, str]] = None,
        default_confidence: float = 0.85,
    ) -> None:
        """Initialize SpacyDetector.

        Args:
            model_name: Name of spaCy model (default: 'en_core_web_lg').
            target_entities: Subset of spaCy entity types to detect.
            type_mapping: Custom mapping dictionary for entity types.
            default_confidence: Default confidence assigned to spaCy NER detections.
        """
        self.model_name = model_name
        self.target_entities = target_entities or SPACY_TARGET_ENTITIES
        self.type_mapping = type_mapping or SPACY_TYPE_MAP
        self.default_confidence = default_confidence

        self._nlp = None
        self._initialized = False

        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initializes spaCy model lazily with fallback to smaller models if required."""
        try:
            import spacy

            # Try requested model (e.g. en_core_web_lg)
            try:
                self._nlp = spacy.load(self.model_name)
                logger.info("Loaded primary spaCy model '%s'.", self.model_name)
            except OSError:
                # Fallback to en_core_web_sm if lg is not downloaded
                logger.warning(
                    "Primary model '%s' not found. Attempting fallback to 'en_core_web_sm'...",
                    self.model_name,
                )
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded fallback spaCy model 'en_core_web_sm'.")

            self._initialized = True
        except Exception as err:
            logger.warning(
                "Failed to initialize spaCy NLP pipeline (%s). Detector will run in fallback mode.",
                err,
            )
            self._nlp = None
            self._initialized = False

    @property
    def is_available(self) -> bool:
        """Returns True if spaCy model is loaded and operational."""
        return self._initialized and self._nlp is not None

    def detect(self, text: str) -> List[Entity]:
        """Scans input text using spaCy NER and returns standardized Entity objects.

        Args:
            text: Raw string document to analyze.

        Returns:
            List of standardized Entity objects.
        """
        if not text or not self.is_available:
            return []

        try:
            doc = self._nlp(text)
            entities: List[Entity] = []

            for ent in doc.ents:
                if ent.label_ not in self.target_entities:
                    continue

                mapped_type = self.type_mapping.get(ent.label_, ent.label_)

                entity = Entity(
                    type=mapped_type,
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=self.default_confidence,
                    category="SPACY_NER",
                )
                entities.append(entity)

            # Sort by start character offset
            entities.sort(key=lambda e: (e.start, -(e.end - e.start)))
            return entities

        except Exception as err:
            logger.error("Error during spaCy NER detection: %s", err)
            return []
