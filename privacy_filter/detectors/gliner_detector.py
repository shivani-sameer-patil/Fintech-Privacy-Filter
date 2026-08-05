"""
GLiNER Detector Module for FinTech Privacy Filter.

Uses the urchade/gliner_large-v2.1 zero-shot NER model to detect
various PII and financial entities, mapping them to standard pipeline Entity formats.
"""

import logging
from typing import Dict, List, Optional

from privacy_filter.detectors.regex_detector import Entity

logger = logging.getLogger(__name__)

# Standard mapping from GLiNER descriptive labels to pipeline Entity types
GLINER_TYPE_MAP: Dict[str, str] = {
    "person": "PERSON",
    "organization": "ORG",
    "phone number": "PHONE",
    "email": "EMAIL",
    "date": "DATE",
    "credit card": "CARD",
    "bank account": "ACCOUNT_NUMBER",
    "aadhaar": "AADHAAR",
    "pan card": "PAN",
    "ifsc code": "IFSC",
    "loan account": "LOAN_ACCOUNT",
    "passport number": "PASSPORT",
    "driving license": "DRIVING_LICENSE",
    "voter id": "VOTER_ID",
}


class GlinerDetector:
    """Named Entity Recognition detector leveraging GLiNER zero-shot NLP models."""

    def __init__(
        self,
        model_name: str = "urchade/gliner_large-v2.1",
        threshold: float = 0.5,
        labels: Optional[List[str]] = None,
        type_mapping: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize GlinerDetector.

        Args:
            model_name: Hugging Face model identifier for GLiNER.
            threshold: Minimum score threshold for entity prediction.
            labels: Custom list of entity labels to search for.
            type_mapping: Custom mapping from GLiNER labels to pipeline Entity types.
        """
        self.model_name = model_name
        self.threshold = threshold
        self.type_mapping = type_mapping or GLINER_TYPE_MAP
        self.labels = labels or list(self.type_mapping.keys())
        self._model = None
        self._initialized = False

        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initializes GLiNER model safely with error handling and fallbacks."""
        try:
            from gliner import GLiNER

            # Load primary model
            self._model = GLiNER.from_pretrained(self.model_name)
            self._initialized = True
            logger.info("Loaded GLiNER model '%s'.", self.model_name)
        except Exception as err:
            logger.warning(
                "Failed to initialize GLiNER model '%s' (%s). Detector will run in fallback mode.",
                self.model_name,
                err,
            )
            self._model = None
            self._initialized = False

    @property
    def is_available(self) -> bool:
        """Returns True if GLiNER model is loaded and operational."""
        return self._initialized and self._model is not None

    def detect(self, text: str) -> List[Entity]:
        """Scans input text using GLiNER NER model.

        Args:
            text: Raw string document to analyze.

        Returns:
            List of standardized Entity objects.
        """
        if not text or not self.is_available:
            return []

        try:
            results = self._model.predict_entities(
                text,
                self.labels,
                threshold=self.threshold,
                flat_ner=True,
            )

            entities: List[Entity] = []
            for res in results:
                label = res.get("label")
                mapped_type = self.type_mapping.get(label, label.upper())

                entity = Entity(
                    type=mapped_type,
                    text=res.get("text"),
                    start=res.get("start"),
                    end=res.get("end"),
                    confidence=float(res.get("score", 1.0)),
                    category="GLINER_NER",
                )
                entities.append(entity)

            # Sort by start offset
            entities.sort(key=lambda e: (e.start, -(e.end - e.start)))
            return entities
        except Exception as err:
            logger.error("Error during GLiNER NER detection: %s", err)
            return []
