"""
Configuration Module for FinTech Privacy Filter.

Centralized dataclass configuration managing pipeline behavior, detector enablement flags,
confidence thresholds, models, and semantic masking tag templates.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from privacy_filter.detectors.masker import DEFAULT_TAG_MAPPING


@dataclass
class PipelineConfig:
    """Dataclass holding all configuration settings for FinTech Privacy Filter pipeline."""

    # Module Enablement Flags
    enable_language_detection: bool = True
    enable_indic_normalization: bool = True
    enable_regex_detection: bool = True
    enable_presidio_detection: bool = True
    enable_spacy_detection: bool = True
    enable_context_classification: bool = True
    enable_keyword_detection: bool = True

    # NLP & Model Parameters
    spacy_model_name: str = "en_core_web_lg"
    presidio_score_threshold: float = 0.4
    min_confidence: float = 0.4
    context_window_size: int = 60
    keyword_detection_threshold: float = 0.6

    # Custom Semantic Tag Mappings
    tag_mapping: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_TAG_MAPPING))

    # Default Language Fallback
    fallback_language: str = "en"
