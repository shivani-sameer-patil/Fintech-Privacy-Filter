"""
spaCy Detector Module for FinTech Privacy Filter.

Uses spaCy's Named Entity Recognition (NER) models (en_core_web_lg) to detect
PERSON, ORG, LOC, DATE, and GPE entities and convert them to standard Entity format.
"""

import logging
import re
from typing import Dict, List, Optional, Set

from privacy_filter.detectors.regex_detector import Entity

logger = logging.getLogger(__name__)

# Default target spaCy entity types
SPACY_TARGET_ENTITIES: Set[str] = {"PERSON", "DATE"}

# Standard mapping from spaCy Entity labels to pipeline Entity types
SPACY_TYPE_MAP: Dict[str, str] = {
    "PERSON": "PERSON",
    "DATE": "DATE",
}

# Honorific prefixes list per script
HONORIFIC_PREFIXES = {
    "en": r"\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Shri\.?|Smt\.?|Kumari\.?|Kumar\.?|Srimati\.?)\b",
    "hi_mr": r"(?:श्री|श्रीमती|कुमार|कुमारी|डॉ\.?)",
    "kn": r"(?:ಶ್ರೀ|ಶ್ರೀಮತಿ|ಡา\.?)",
    "ta": r"(?:திரு|திருமதி|டாக்டர்)",
    "te": r"(?:శ్రీ|శ్రీమతి|డాక్టర్)",
    "ml": r"(?:ശ്രീ|ശ്രീമതി|ഡോക്ടർ)",
    "bn_as": r"(?:শ্রী|শ্রীমতী|ডা\.?)",
    "gu": r"(?:શ્રી|શ્રીમતી|ડો\.?)",
    "pa": r"(?:ਸ਼੍ਰੀ|ਸ਼੍ਰੀਮਤੀ|ਡਾ\.?)",
    "or": r"(?:ଶ୍ରୀ|ଶ୍ରୀମତୀ|ଡା\.?)",
    "ur": r"(?:جناب|محترم|ڈاکٹر)",
}

# Compile patterns looking for honorific prefix + space + name words in respective scripts
HYBRID_NAME_PATTERNS = [
    re.compile(rf'{HONORIFIC_PREFIXES["en"]}\s+([A-Z][a-zA-Z\.]+)\s*([A-Z][a-zA-Z\.]+)?\s*([A-Z][a-zA-Z\.]+)?'),
    re.compile(rf'{HONORIFIC_PREFIXES["hi_mr"]}\s+([\u0900-\u097F]+(?:\s+[\u0900-\u097F]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["kn"]}\s+([\u0C80-\u0CFF]+(?:\s+[\u0C80-\u0CFF]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["ta"]}\s+([\u0B80-\u0BFF]+(?:\s+[\u0B80-\u0BFF]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["te"]}\s+([\u0C00-\u0C7F]+(?:\s+[\u0C00-\u0C7F]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["ml"]}\s+([\u0D00-\u0D7F]+(?:\s+[\u0D00-\u0D7F]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["bn_as"]}\s+([\u0980-\u09FF]+(?:\s+[\u0980-\u09FF]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["gu"]}\s+([\u0A80-\u0AFF]+(?:\s+[\u0A80-\u0AFF]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["pa"]}\s+([\u0A00-\u0A7F]+(?:\s+[\u0A00-\u0A7F]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["or"]}\s+([\u0B00-\u0B7F]+(?:\s+[\u0B00-\u0B7F]+){{0,2}})'),
    re.compile(rf'{HONORIFIC_PREFIXES["ur"]}\s+([\u0600-\u06FF]+(?:\s+[\u0600-\u06FF]+){{0,2}})'),
]


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
        """Scans input text using spaCy NER and hybrid name regexes.

        Args:
            text: Raw string document to analyze.

        Returns:
            List of standardized Entity objects.
        """
        if not text:
            return []

        entities: List[Entity] = []

        # 1. Run hybrid name matching regexes (doesn't require spaCy model to be loaded)
        for pattern in HYBRID_NAME_PATTERNS:
            for match in pattern.finditer(text):
                matched_text = match.group(0).strip()
                
                # Strip common grammatical particles/postpositions in Indian scripts
                particles = {"का", "की", "के", "ने", "को", "से", "में", "पर", "ನ", "ನಿಗೆ", "ಯ", "ను", "కు", "తో", "లో"}
                words = matched_text.split()
                while words and words[-1] in particles:
                    words.pop()
                matched_text = " ".join(words)
                
                start, end = match.span()
                entity = Entity(
                    type="PERSON",
                    text=matched_text,
                    start=start,
                    end=start + len(matched_text),
                    confidence=0.95,
                    category="HYBRID_NAME_REGEX",
                )
                entities.append(entity)

        # 2. Run spaCy model NER if available
        if self.is_available:
            try:
                doc = self._nlp(text)
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
            except Exception as err:
                logger.error("Error during spaCy NER detection: %s", err)

        # Sort by start character offset
        entities.sort(key=lambda e: (e.start, -(e.end - e.start)))
        return entities
