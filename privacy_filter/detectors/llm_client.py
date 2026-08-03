import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMClassifierClient:
    """Lightweight, offline-focused local LLM validator client for domain disambiguation."""

    def __init__(
        self,
        provider: str = "ollama",
        model_name: str = "qwen2.5:1.5b",
        api_url: str = "http://localhost:11434/api/generate",
        timeout: float = 15.0,
    ) -> None:
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_url = api_url
        self.timeout = timeout

    def generate_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Sends generate prompt to the local LLM and returns the parsed JSON response.

        Returns None on timeout, connection error, or invalid JSON layout.
        """
        if self.provider == "mock":
            # For offline unit tests
            prompt_lower = prompt.lower()
            if "entities" in prompt_lower:
                mock_entities = []
                if "4567 8912 3456" in prompt_lower or "456789123456" in prompt_lower:
                    mock_entities.append({
                        "text": "4567 8912 3456",
                        "type": "AADHAAR",
                        "confidence": 0.95
                    })
                if "123456789012" in prompt_lower:
                    mock_entities.append({
                        "text": "123456789012",
                        "type": "ACCOUNT_NUMBER",
                        "confidence": 0.90
                    })
                if "2345 6789 0123" in prompt_lower:
                    mock_entities.append({
                        "text": "2345 6789 0123",
                        "type": "AADHAAR",
                        "confidence": 0.95
                    })
                if "1234567890" in prompt_lower:
                    mock_entities.append({
                        "text": "1234567890",
                        "type": "ACCOUNT_NUMBER",
                        "confidence": 0.90
                    })
                return {"entities": mock_entities}

            if "4567 8912 3456" in prompt_lower or "456789123456" in prompt_lower:
                return {
                    "disambiguated_type": "AADHAAR",
                    "confidence": 0.95,
                    "reasoning": "Explicit mock AADHAAR pattern matched."
                }
            if "123456789012" in prompt_lower or "1234567890" in prompt_lower:
                return {
                    "disambiguated_type": "ACCOUNT_NUMBER",
                    "confidence": 0.90,
                    "reasoning": "Explicit mock ACCOUNT_NUMBER pattern matched."
                }
            return {
                "disambiguated_type": "UNKNOWN_NUMERIC_ID",
                "confidence": 0.50,
                "reasoning": "Fallback mock type."
            }

        if self.provider == "ollama":
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "format": "json",
                "stream": False,
            }
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    res_data = response.json()
                    response_text = res_data.get("response", "").strip()
                    if not response_text:
                        return None
                    return json.loads(response_text)
                else:
                    logger.warning(
                        f"Ollama returned HTTP status {response.status_code}: {response.text}"
                    )
            except requests.RequestException as e:
                logger.warning(f"Ollama connection error: {e}")
            except json.JSONDecodeError as e:
                logger.warning(f"Ollama returned invalid JSON text: {e}")

        return None
