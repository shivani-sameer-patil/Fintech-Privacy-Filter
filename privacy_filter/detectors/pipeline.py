"""
Master Pipeline Module for FinTech Privacy Filter.

Orchestrates the complete 10-step end-to-end preprocessing workflow:
Input -> Language Detection -> Indic Normalization -> Regex Detection -> Presidio Detection
-> spaCy Detection -> Context Classification -> Entity Merging -> Masking -> Output.
"""

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from privacy_filter.config import PipelineConfig
from privacy_filter.detectors.context_classifier import ContextClassifier
from privacy_filter.detectors.indic_normalizer import IndicNormalizer
from privacy_filter.detectors.language_detector import (
    LanguageDetector,
    LanguageResult,
)
from privacy_filter.detectors.masker import Masker, MaskResult
from privacy_filter.detectors.merger import EntityMerger
from privacy_filter.detectors.presidio_detector import PresidioDetector
from privacy_filter.detectors.regex_detector import Entity, RegexDetector
from privacy_filter.detectors.spacy_detector import SpacyDetector
from privacy_filter.detectors.multilingual_keyword_detector import MultilingualKeywordDetector


@dataclass
class PipelineOutput:
    """Structure holding complete end-to-end pipeline output and processing metrics.

    Attributes:
        original_text: Unmodified input document string.
        normalized_text: Numerically normalized string (ASCII digits).
        masked_text: Final sanitized string with sensitive entities replaced by placeholders.
        language: LanguageResult object holding detected language & script.
        detected_entities: List of non-overlapping merged Entity objects.
        entities_masked_count: Total count of masked entities.
        entity_counts: Frequency map of masked entity types.
        processing_time_ms: Total pipeline execution wall-clock time in milliseconds.
    """
    original_text: str
    normalized_text: str
    masked_text: str
    language: LanguageResult
    detected_entities: List[Entity]
    entities_masked_count: int
    entity_counts: Dict[str, int]
    processing_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Returns complete pipeline results as a serializable dictionary."""
        return {
            "original_text": self.original_text,
            "normalized_text": self.normalized_text,
            "masked_text": self.masked_text,
            "language": self.language.to_dict(),
            "detected_entities": [e.to_dict() for e in self.detected_entities],
            "entities_masked_count": self.entities_masked_count,
            "entity_counts": self.entity_counts,
            "processing_time_ms": round(self.processing_time_ms, 2),
        }


class FinTechPrivacyPipeline:
    """Master preprocessing pipeline orchestrating end-to-end PII masking."""

    def __init__(self, config: Optional[PipelineConfig] = None) -> None:
        """Initialize FinTechPrivacyPipeline with configuration settings.

        Args:
            config: Optional PipelineConfig object. Uses defaults if None.
        """
        self.config = config or PipelineConfig()

        # Initialize pipeline detector modules
        self.language_detector = (
            LanguageDetector(fallback_language=self.config.fallback_language)
            if self.config.enable_language_detection
            else None
        )

        self.indic_normalizer = (
            IndicNormalizer()
            if self.config.enable_indic_normalization
            else None
        )

        self.regex_detector = (
            RegexDetector(min_confidence=self.config.min_confidence)
            if self.config.enable_regex_detection
            else None
        )

        self.presidio_detector = (
            PresidioDetector(score_threshold=self.config.presidio_score_threshold)
            if self.config.enable_presidio_detection
            else None
        )

        self.spacy_detector = (
            SpacyDetector(model_name=self.config.spacy_model_name)
            if self.config.enable_spacy_detection
            else None
        )

        self.context_classifier = (
            ContextClassifier(window_size=self.config.context_window_size)
            if self.config.enable_context_classification
            else None
        )

        self.keyword_detector = (
            MultilingualKeywordDetector(
                window_size=self.config.context_window_size,
                min_confidence=self.config.keyword_detection_threshold,
            )
            if self.config.enable_keyword_detection
            else None
        )

        self.merger = EntityMerger()
        self.masker = Masker(tag_mapping=self.config.tag_mapping)

    def process(self, text: str) -> PipelineOutput:
        """Executes the master 10-step FinTech privacy filtering pipeline.

        Args:
            text: Input raw document string (Email, Chat, Bank Statement, KYC, etc.).

        Returns:
            PipelineOutput object containing sanitized text and detection metadata.
        """
        start_time = time.perf_counter()

        if not text or not text.strip():
            empty_lang = (
                self.language_detector.detect("")
                if self.language_detector
                else LanguageResult("en", "English", 1.0, "Latin")
            )
            return PipelineOutput(
                original_text=text or "",
                normalized_text=text or "",
                masked_text=text or "",
                language=empty_lang,
                detected_entities=[],
                entities_masked_count=0,
                entity_counts={},
                processing_time_ms=0.0,
            )

        # ---------------------------------------------------------------------
        # Step 1: Language Detection
        # ---------------------------------------------------------------------
        language_res = (
            self.language_detector.detect(text)
            if self.language_detector
            else LanguageResult("en", "English", 1.0, "Latin")
        )

        # ---------------------------------------------------------------------
        # Step 2: Indic Numeral Normalization
        # ---------------------------------------------------------------------
        normalized_text = (
            self.indic_normalizer.normalize_text(text)
            if self.indic_normalizer
            else text
        )

        # ---------------------------------------------------------------------
        # Step 3, 4, 5: Parallel Detector Engine Executions
        # ---------------------------------------------------------------------
        regex_entities: List[Entity] = (
            self.regex_detector.detect(normalized_text)
            if self.regex_detector
            else []
        )

        presidio_entities: List[Entity] = (
            self.presidio_detector.detect(normalized_text, language=language_res.language_code)
            if self.presidio_detector and self.presidio_detector.is_available
            else []
        )

        spacy_entities: List[Entity] = (
            self.spacy_detector.detect(normalized_text)
            if self.spacy_detector and self.spacy_detector.is_available
            else []
        )

        keyword_entities: List[Entity] = (
            self.keyword_detector.detect(normalized_text)
            if self.keyword_detector
            else []
        )

        # ---------------------------------------------------------------------
        # Step 6: Context Classification & Disambiguation
        # ---------------------------------------------------------------------
        all_candidate_entities = regex_entities + presidio_entities + spacy_entities + keyword_entities
        if self.context_classifier and all_candidate_entities:
            classified_entities = self.context_classifier.classify_all(
                all_candidate_entities, normalized_text
            )
        else:
            classified_entities = all_candidate_entities

        # ---------------------------------------------------------------------
        # Step 7: Entity Merging & Overlap Resolution
        # ---------------------------------------------------------------------
        merged_entities = self.merger.merge(classified_entities)

        # ---------------------------------------------------------------------
        # Step 8: Text Masking
        # ---------------------------------------------------------------------
        mask_res: MaskResult = self.masker.mask(normalized_text, merged_entities)

        # ---------------------------------------------------------------------
        # Step 9 & 10: Final Metrics & Pipeline Output
        # ---------------------------------------------------------------------
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return PipelineOutput(
            original_text=text,
            normalized_text=normalized_text,
            masked_text=mask_res.masked_text,
            language=language_res,
            detected_entities=merged_entities,
            entities_masked_count=mask_res.entities_masked,
            entity_counts=mask_res.entity_counts,
            processing_time_ms=elapsed_ms,
        )
