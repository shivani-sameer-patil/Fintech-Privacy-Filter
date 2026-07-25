"""
Multilingual Keyword Classifier and Detector Module.

Implements a trainable context-aware classifier using weighted keyword proximity scoring,
and a detector that identifies generic sensitive patterns and classifies them using context.
"""

import re
from typing import Dict, List, Optional, Set, Tuple

from privacy_filter.detectors.context_classifier import MULTILINGUAL_KEYWORDS
from privacy_filter.detectors.regex_detector import Entity


def tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric words, supporting multilingual Unicode."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return [w for w in cleaned.split() if w]


def validate_entity_format(entity_type: str, value: str) -> bool:
    """Performs structural/format checks to reduce false positives for predicted entity types."""
    cleaned_digits = "".join(c for c in value if c.isdigit())

    if entity_type == "AADHAAR":
        return len(cleaned_digits) == 12
    elif entity_type in ("OTP", "MPIN", "TRANSACTION_PIN"):
        # Enforce that PINs and OTPs are purely numeric (allowing digits, optional spaces/hyphens)
        if not all(c.isdigit() or c.isspace() or c == "-" for c in value):
            return False
        if not cleaned_digits:
            return False
        if entity_type == "OTP":
            return 4 <= len(cleaned_digits) <= 8
        else:  # MPIN, TRANSACTION_PIN
            return 4 <= len(cleaned_digits) <= 6
    elif entity_type == "CHEQUE_NUMBER":
        return len(cleaned_digits) == 6
    elif entity_type == "PAN":
        # Standard PAN is alphanumeric and 10 chars
        return len(value) == 10 and any(c.isdigit() for c in value) and any(c.isalpha() for c in value)
    elif entity_type in ("ACCOUNT_NUMBER", "LOAN_ACCOUNT"):
        return 9 <= len(cleaned_digits) <= 18
    elif entity_type == "POLICY_NUMBER":
        return 6 <= len(value) <= 16 and any(c.isdigit() for c in value)
    elif entity_type == "MICR":
        return len(cleaned_digits) == 9
    elif entity_type == "IFSC":
        return len(value) == 11 and any(c.isdigit() for c in value)
    elif entity_type == "SWIFT":
        if len(value) not in (8, 11):
            return False
        country_code = value[4:6].upper()
        valid_countries = {
            "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ",
            "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS",
            "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN",
            "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE",
            "EG", "EH", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF",
            "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM",
            "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM",
            "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC",
            "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK",
            "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA",
            "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG",
            "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW",
            "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS",
            "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO",
            "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI",
            "VN", "VU", "WF", "WS", "YE", "YT", "ZA", "ZM", "ZW"
        }
        return country_code in valid_countries
    elif entity_type == "CARD":
        return 13 <= len(cleaned_digits) <= 19
    elif entity_type == "CVV":
        return len(cleaned_digits) in (3, 4)
    elif entity_type == "UPI":
        return "@" in value
    return True


class MultilingualKeywordClassifier:
    """Classifier utilizing weighted phrase and term matching on multilingual keywords."""

    def __init__(self, keyword_dict: Optional[Dict[str, Dict[str, List[str]]]] = None) -> None:
        """Initialize MultilingualKeywordClassifier."""
        self.keyword_dict = keyword_dict if keyword_dict is not None else MULTILINGUAL_KEYWORDS
        self.class_keywords: Dict[str, List[str]] = {}

        # Build initial keyword map
        self._build_keyword_map()

    def _build_keyword_map(self) -> None:
        """Flattens the structured keyword dictionary into sorted lowercase search lists."""
        self.class_keywords = {}
        for entity_type, lang_map in self.keyword_dict.items():
            kws = []
            for lang, kw_list in lang_map.items():
                for kw in kw_list:
                    kw_clean = kw.strip().lower()
                    if kw_clean:
                        kws.append(kw_clean)
            self.class_keywords[entity_type] = sorted(list(set(kws)), key=len, reverse=True)

    def train(self, training_data: List[Tuple[str, str]]) -> None:
        """Trains the classifier by extracting terms/phrases from custom training samples.

        Args:
            training_data: A list of (sentence_text, entity_type) tuples.
        """
        self.class_keywords = {}
        for text, entity_type in training_data:
            if entity_type not in self.class_keywords:
                self.class_keywords[entity_type] = []
            # Extract individual words
            words = tokenize(text)
            self.class_keywords[entity_type].extend(words)
            # Extract full text as a keyword phrase
            self.class_keywords[entity_type].append(text.lower().strip())

        # Deduplicate and sort keywords
        for c in self.class_keywords:
            self.class_keywords[c] = sorted(list(set(self.class_keywords[c])), key=len, reverse=True)

    def predict(self, text: str) -> Optional[Tuple[str, float]]:
        """Predicts the entity type by scoring matches in the context text."""
        if not self.class_keywords:
            return None

        text_lower = text.lower()
        scores: Dict[str, float] = {}

        # Non-discriminative generic words are weighted lower to prevent false-positive dominance
        generic_words = {
            "number", "no", "card", "code", "details", "premium", "savings", "is", "the", "a",
            "an", "your", "my", "our", "please", "enter", "to", "for", "in", "of", "and", "or",
            "on", "at", "this", "that", "value", "id", "info", "data", "here", "been", "has", "it"
        }

        for entity_type, keywords in self.class_keywords.items():
            class_score = 0.0

            for kw in keywords:
                # Require word boundaries for short keywords (len < 4) to prevent substring pollution
                if len(kw) < 4:
                    pattern = r"\b" + re.escape(kw) + r"\b"
                    matches = list(re.finditer(pattern, text_lower))
                    if matches:
                        weight = 0.5 if kw in generic_words else 1.5
                        class_score += len(matches) * len(kw) * weight
                else:
                    # Substring match is suitable for longer keywords and phrases
                    pos = text_lower.find(kw)
                    count = 0
                    while pos != -1:
                        count += 1
                        pos = text_lower.find(kw, pos + 1)
                    if count > 0:
                        weight = 0.5 if kw in generic_words else 1.5
                        if " " in kw:
                            weight *= 2.0  # Double weight for multi-word phrase match
                        class_score += count * len(kw) * weight

            if class_score > 0:
                scores[entity_type] = class_score

        if not scores:
            return None

        best_class = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = scores[best_class] / max(1e-9, total_score)

        return best_class, confidence


class MultilingualKeywordDetector:
    """Pipeline-compatible detector that finds generic codes and classifies them using context."""

    def __init__(
        self,
        classifier: Optional[MultilingualKeywordClassifier] = None,
        window_size: int = 60,
        min_confidence: float = 0.6,
    ) -> None:
        """Initialize MultilingualKeywordDetector."""
        self.classifier = classifier or MultilingualKeywordClassifier()
        self.window_size = window_size
        self.min_confidence = min_confidence

        # Generic patterns to find numeric/alphanumeric candidates:
        # 1. Numeric tokens: 4 to 18 digits
        # 2. Alphanumeric tokens containing at least one digit: 4 to 20 chars
        # 3. Uppercase codes: 8 or 11 chars (matches SWIFT code length constraints)
        self.candidate_regex = re.compile(
            r"\b(?:\d{4,18}|(?=[A-Za-z-]*\d)[A-Za-z0-9-]{4,20}|[A-Z]{8}|[A-Z]{11})\b"
        )

    def detect(self, text: str) -> List[Entity]:
        """Scans input text, classifies matching generic values based on context, and returns entities."""
        if not text:
            return []

        entities: List[Entity] = []

        for match in self.candidate_regex.finditer(text):
            value = match.group(0)
            start, end = match.span()

            # Extract surrounding context, excluding the value itself to avoid target value bias
            left_context = text[max(0, start - self.window_size) : start]
            right_context = text[end : min(len(text), end + self.window_size)]
            context_text = left_context + " " + right_context

            prediction = self.classifier.predict(context_text)
            if prediction:
                predicted_class, confidence = prediction
                if confidence >= self.min_confidence:
                    # Validate candidate structure to reduce false positives
                    if validate_entity_format(predicted_class, value):
                        entity = Entity(
                            type=predicted_class,
                            text=value,
                            start=start,
                            end=end,
                            confidence=confidence,
                            category="KEYWORD_CONTEXT",
                        )
                        entities.append(entity)

        return entities
