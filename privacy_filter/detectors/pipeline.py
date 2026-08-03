"""
Master Pipeline Module for FinTech Privacy Filter.

Orchestrates the complete 10-step end-to-end preprocessing workflow:
Input -> Language Detection -> Indic Normalization -> Regex Detection -> Presidio Detection
-> spaCy Detection -> Context Classification -> Entity Merging -> Masking -> Output.
"""

import time
from concurrent.futures import ThreadPoolExecutor
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
from privacy_filter.detectors.llm_detector import LLMDetector


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
    detector_latencies: Dict[str, float] = field(default_factory=dict)

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
            "detector_latencies": {k: round(v, 2) for k, v in self.detector_latencies.items()},
        }


def _run_timed_detector(detector_func, *args, **kwargs):
    """Executes a detector function and returns its results along with wall-clock latency in milliseconds."""
    start = time.perf_counter()
    result = detector_func(*args, **kwargs)
    latency_ms = (time.perf_counter() - start) * 1000.0
    return result, latency_ms


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
            ContextClassifier(
                window_size=self.config.context_window_size,
                config=self.config
            )
            if self.config.enable_context_classification
            else None
        )
        if self.context_classifier:
            self.context_classifier.llm_client = None

        self.keyword_detector = (
            MultilingualKeywordDetector(
                window_size=self.config.context_window_size,
                min_confidence=self.config.keyword_detection_threshold,
            )
            if self.config.enable_keyword_detection
            else None
        )

        self.llm_detector = (
            LLMDetector(config=self.config)
            if self.config.enable_llm_classifier
            else None
        )

        self.merger = EntityMerger()
        self.masker = Masker(tag_mapping=self.config.tag_mapping)
        self.executor = ThreadPoolExecutor(max_workers=5)

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
                detector_latencies={},
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
        futures = {}

        if self.regex_detector:
            futures["regex"] = self.executor.submit(
                _run_timed_detector, self.regex_detector.detect, normalized_text
            )

        if self.presidio_detector and self.presidio_detector.is_available and language_res.language_code == "en":
            futures["presidio"] = self.executor.submit(
                _run_timed_detector, self.presidio_detector.detect, normalized_text, language=language_res.language_code
            )

        if self.spacy_detector:
            futures["spacy"] = self.executor.submit(
                _run_timed_detector, self.spacy_detector.detect, normalized_text
            )

        if self.keyword_detector:
            futures["keyword"] = self.executor.submit(
                _run_timed_detector, self.keyword_detector.detect, normalized_text
            )

        if self.llm_detector:
            futures["llm"] = self.executor.submit(
                _run_timed_detector, self.llm_detector.detect, normalized_text
            )

        regex_entities, regex_time = futures["regex"].result() if "regex" in futures else ([], 0.0)
        presidio_entities, presidio_time = futures["presidio"].result() if "presidio" in futures else ([], 0.0)
        spacy_entities, spacy_time = futures["spacy"].result() if "spacy" in futures else ([], 0.0)
        keyword_entities, keyword_time = futures["keyword"].result() if "keyword" in futures else ([], 0.0)
        llm_entities, llm_time = futures["llm"].result() if "llm" in futures else ([], 0.0)



        # ---------------------------------------------------------------------
        # Step 6: Context Classification & Disambiguation
        # ---------------------------------------------------------------------
        all_candidate_entities = regex_entities + presidio_entities + spacy_entities + keyword_entities + llm_entities
        if language_res.language_code != "en":
            # Keep PERSON entities in non-English text only if they were matched by the hybrid name detector
            all_candidate_entities = [
                e for e in all_candidate_entities 
                if e.type != "PERSON" or e.category == "HYBRID_NAME_REGEX"
            ]

        if self.context_classifier and all_candidate_entities:
            self.context_classifier.llm_execution_time_ms = 0.0
            classified_entities = self.context_classifier.classify_all(
                all_candidate_entities, normalized_text
            )
            # Filter out PINCODE entities to prevent them from being masked
            classified_entities = [e for e in classified_entities if e.type != "PINCODE"]
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

        llm_time = 0.0
        if self.context_classifier:
            llm_time = getattr(self.context_classifier, "llm_execution_time_ms", 0.0)

        detector_latencies = {
            "regex": regex_time,
            "presidio": presidio_time,
            "spacy": spacy_time,
            "keyword": keyword_time,
            "llm": llm_time,
        }

        return PipelineOutput(
            original_text=text,
            normalized_text=normalized_text,
            masked_text=mask_res.masked_text,
            language=language_res,
            detected_entities=merged_entities,
            entities_masked_count=mask_res.entities_masked,
            entity_counts=mask_res.entity_counts,
            processing_time_ms=elapsed_ms,
            detector_latencies=detector_latencies,
        )
