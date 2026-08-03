import logging
import re
from typing import List, Optional, Any

from privacy_filter.detectors.regex_detector import Entity
from privacy_filter.detectors.llm_client import LLMClassifierClient

logger = logging.getLogger(__name__)


class LLMDetector:
    """Parallel local LLM-backed PII detector using structured zero-shot classification."""

    def __init__(self, config: Optional[Any] = None) -> None:
        self.config = config
        self.llm_client = None
        if self.config and getattr(self.config, "enable_llm_classifier", False):
            self.llm_client = LLMClassifierClient(
                provider=self.config.llm_provider,
                model_name=self.config.llm_model_name,
                api_url=self.config.llm_api_url,
                timeout=self.config.llm_timeout_seconds,
            )

    def detect(self, text: str) -> List[Entity]:
        """Detects sensitive entities using local LLM zero-shot extraction."""
        if not text or not self.llm_client:
            return []

        type_descriptions = {
            "AADHAAR": "12-digit Indian national identity card number (UID / Aadhaar / आधार / ಆಧಾರ್)",
            "ACCOUNT_NUMBER": "Bank account number (savings, checking, deposit, खाता, ಖಾತೆ, bank, IFSC)",
            "LOAN_ACCOUNT": "Loan account number (mortgage, personal loan, ऋण, ಸಾಲ)",
            "PHONE": "10-digit telephone / mobile phone number",
            "PAN": "Permanent Account Number card identifier",
            "EMAIL": "Email address",
        }

        type_options_list = [f'- "{k}": {v}' for k, v in type_descriptions.items()]
        type_options = "\n".join(type_options_list)

        prompt = f"""You are a high-performance PII detector. Analyze the following text and extract all sensitive PII entities.

Guidelines:
- If the text mentions a 12-digit sequence of numbers described by or near words like "national identity card", "UID", "Aadhaar", "आधार", or "ಆಧಾರ್", extract it as "AADHAAR".
- If the text mentions a number described by or near words like "bank account", "savings account", "checking account", "खाता", "खाते", "ಖಾತೆ", "ಖಾತೆ ಸಂಖ್ಯೆ", "खाते क्रमांक", or near terms like "bank", "IFSC", "बैंक", extract it as "ACCOUNT_NUMBER".
- If the text mentions a number described by or near words like "loan", "lending", "mortgage", "ऋण", or "ಸಾಲ", extract it as "LOAN_ACCOUNT".
- For any PAN card strings, extract them as "PAN".
- For phone numbers, extract them as "PHONE".
- For emails, extract them as "EMAIL".

For each extracted entity, return the exact text match from the document and the classified entity type.
Respond ONLY with a JSON object in this format:
{{
  "entities": [
    {{
      "text": "exact substring from text",
      "type": "entity type (e.g., AADHAAR, ACCOUNT_NUMBER, PAN, PHONE, EMAIL)",
      "confidence": 0.0 to 1.0,
      "reasoning": "brief explanation"
    }}
  ]
}}

Text to analyze:
"{text}"
"""
        detected_entities = []
        try:
            res_json = self.llm_client.generate_json(prompt)
            if res_json and isinstance(res_json, dict) and "entities" in res_json:
                for ent_info in res_json["entities"]:
                    ent_text = ent_info.get("text")
                    ent_type = ent_info.get("type")
                    confidence = ent_info.get("confidence", 0.8)

                    if not ent_text or not ent_type:
                        continue

                    # Search for the exact string within the normalized text
                    escaped_text = re.escape(ent_text.strip())
                    if not escaped_text:
                        continue
                    for match in re.finditer(escaped_text, text):
                        start, end = match.span()
                        detected_entities.append(
                            Entity(
                                type=ent_type,
                                text=ent_text,
                                start=start,
                                end=end,
                                confidence=confidence,
                                category=f"LLM_DETECTED_{self.llm_client.provider.upper()}",
                            )
                        )
        except Exception as e:
            logger.error(f"LLMDetector classification failed: {e}")

        return detected_entities
