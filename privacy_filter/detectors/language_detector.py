"""
Language Detector Module for FinTech Privacy Filter.

Automatically detects English and 22 official Indian languages using Unicode script block
analysis combined with n-gram probabilistic language identification.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Supported Language Code to Language Name Mapping
LANGUAGE_INFO: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "script": "Latin"},
    "hi": {"name": "Hindi", "script": "Devanagari"},
    "kn": {"name": "Kannada", "script": "Kannada"},
    "ta": {"name": "Tamil", "script": "Tamil"},
    "te": {"name": "Telugu", "script": "Telugu"},
    "ml": {"name": "Malayalam", "script": "Malayalam"},
    "gu": {"name": "Gujarati", "script": "Gujarati"},
    "mr": {"name": "Marathi", "script": "Devanagari"},
    "pa": {"name": "Punjabi", "script": "Gurmukhi"},
    "bn": {"name": "Bengali", "script": "Bengali"},
    "or": {"name": "Odia", "script": "Odia"},
    "as": {"name": "Assamese", "script": "Bengali"},
    "ur": {"name": "Urdu", "script": "Perso-Arabic"},
    "kok": {"name": "Konkani", "script": "Devanagari"},
    "sd": {"name": "Sindhi", "script": "Perso-Arabic"},
    "ks": {"name": "Kashmiri", "script": "Perso-Arabic"},
    "doi": {"name": "Dogri", "script": "Devanagari"},
    "brx": {"name": "Bodo", "script": "Devanagari"},
    "sat": {"name": "Santali", "script": "Ol Chiki"},
    "mai": {"name": "Maithili", "script": "Devanagari"},
    "mni": {"name": "Manipuri", "script": "Meitei Mayek"},
    "ne": {"name": "Nepali", "script": "Devanagari"},
}

# Unicode Script Range Definitions for Indian Scripts
UNICODE_SCRIPT_RANGES: List[Tuple[int, int, str, str]] = [
    (0x0900, 0x097F, "Devanagari", "hi"),  # Devanagari (Hindi, Marathi, Konkani, Dogri, Bodo, Maithili, Nepali)
    (0x0980, 0x09FF, "Bengali", "bn"),     # Bengali & Assamese
    (0x0A00, 0x0A7F, "Gurmukhi", "pa"),    # Punjabi (Gurmukhi)
    (0x0A80, 0x0AFF, "Gujarati", "gu"),    # Gujarati
    (0x0B00, 0x0B7F, "Odia", "or"),        # Odia
    (0x0B80, 0x0BFF, "Tamil", "ta"),       # Tamil
    (0x0C00, 0x0C7F, "Telugu", "te"),      # Telugu
    (0x0C80, 0x0CFF, "Kannada", "kn"),     # Kannada
    (0x0D00, 0x0D7F, "Malayalam", "ml"),   # Malayalam
    (0x0600, 0x06FF, "Perso-Arabic", "ur"),# Urdu, Kashmiri, Sindhi
    (0x1C50, 0x1C7F, "Ol Chiki", "sat"),   # Santali (Ol Chiki)
    (0xABC0, 0xABFF, "Meitei Mayek", "mni"),# Manipuri (Meitei Mayek)
]


@dataclass
class LanguageResult:
    """Structure holding language detection outputs.

    Attributes:
        language_code: ISO 639-1 / 639-3 code (e.g. 'hi', 'en', 'kn').
        language_name: Full English name of detected language (e.g. 'Hindi', 'English').
        confidence: Confidence score float between 0.0 and 1.0.
        script_name: Primary Unicode script name (e.g. 'Devanagari', 'Kannada').
    """
    language_code: str
    language_name: str
    confidence: float
    script_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Returns language detection result as standard dictionary."""
        return {
            "language_code": self.language_code,
            "language_name": self.language_name,
            "confidence": round(self.confidence, 4),
            "script_name": self.script_name,
        }


class LanguageDetector:
    """Intelligent language detector for English and Indian multilingual documents."""

    def __init__(self, fallback_language: str = "en") -> None:
        """Initialize LanguageDetector.

        Args:
            fallback_language: ISO language code to return when text contains no script signals.
        """
        self.fallback_language = fallback_language
        try:
            from langdetect import DetectorFactory
            DetectorFactory.seed = 0
        except ImportError:
            pass

    def _detect_by_unicode_script(self, text: str) -> Optional[Tuple[str, str, float]]:
        """Analyzes Unicode codepoints to determine script frequencies."""
        script_counts: Dict[str, int] = {}
        script_to_lang: Dict[str, str] = {}
        total_letters = 0

        for char in text:
            code = ord(char)
            # Skip spaces, digits, ASCII punctuation
            if char.isspace() or char.isdigit() or (code < 128 and not char.isalpha()):
                continue

            total_letters += 1

            matched_script = False
            for start, end, script_name, lang_code in UNICODE_SCRIPT_RANGES:
                if start <= code <= end:
                    script_counts[script_name] = script_counts.get(script_name, 0) + 1
                    script_to_lang[script_name] = lang_code
                    matched_script = True
                    break

            if not matched_script and char.isalpha() and code < 128:
                script_counts["Latin"] = script_counts.get("Latin", 0) + 1
                script_to_lang["Latin"] = "en"

        if total_letters == 0 or not script_counts:
            return None

        primary_script = max(script_counts, key=script_counts.get)
        match_count = script_counts[primary_script]
        confidence = match_count / total_letters
        detected_lang = script_to_lang.get(primary_script, "en")

        return detected_lang, primary_script, confidence

    def detect(self, text: str) -> LanguageResult:
        """Detects the primary language of the input text.

        Args:
            text: Input string document to analyze.

        Returns:
            LanguageResult object containing language code, name, confidence, and script.
        """
        if not text or not text.strip():
            info = LANGUAGE_INFO.get(self.fallback_language, {"name": "English", "script": "Latin"})
            return LanguageResult(
                language_code=self.fallback_language,
                language_name=info["name"],
                confidence=1.0,
                script_name=info["script"],
            )

        # 1. Unicode Script Block Analysis
        script_result = self._detect_by_unicode_script(text)
        if script_result:
            lang_code, script_name, script_confidence = script_result

            # Attempt fine-grained language identification library fallback if available
            try:
                from langdetect import detect_langs
                langs = detect_langs(text)
                if langs:
                    top = langs[0]
                    # Validate if detected lang matches info mapping
                    if top.lang in LANGUAGE_INFO:
                        lang_code = top.lang
                        script_confidence = max(script_confidence, float(top.prob))
            except Exception:
                pass  # Fall back directly to deterministic script result

            info = LANGUAGE_INFO.get(
                lang_code, {"name": lang_code.upper(), "script": script_name}
            )
            return LanguageResult(
                language_code=lang_code,
                language_name=info["name"],
                confidence=min(1.0, script_confidence),
                script_name=script_name,
            )

        # 2. Default Fallback
        fallback_info = LANGUAGE_INFO.get(
            self.fallback_language, {"name": "English", "script": "Latin"}
        )
        return LanguageResult(
            language_code=self.fallback_language,
            language_name=fallback_info["name"],
            confidence=0.5,
            script_name=fallback_info["script"],
        )
