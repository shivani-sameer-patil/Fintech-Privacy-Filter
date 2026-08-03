import sys
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline

# Replicate the input text from the second screenshot
text = """===============================
PUNJABI
===============================

ਗਾਹਕ ਦਾ ਨਾਮ: ਰਾਹੁਲ ਸ਼ਰਮਾ
ਗਾਹਕ ਦਾ ਨਾਮ: ਰਾਹੁਲ ਸ਼ਰਮਾ

ਤਨਖਾਹ: ₹80,000
ਤਨਖਾਹ: ₹80,000

===============================
URDU
===============================

صارف کا نام: راول شرما
صارف کا نام: راول شرما

تنخواہ: 80,000 روپے
تنخواہ: 80,000 روپے
"""

pipeline = FinTechPrivacyPipeline()
res = pipeline.process(text)

output_lines = []
def log(msg):
    output_lines.append(msg)

log(f"Language Detected: {res.language.language_code} ({res.language.language_name})")
log(f"Masked Text:\n{res.masked_text}\n")

log("Entities detected:")
for e in res.detected_entities:
    log(f"  Type: {e.type} | Text: '{e.text}' | Start: {e.start} | End: {e.end} | Conf: {e.confidence} | Cat: {e.category}")

Path("check_multilingual_output.txt").write_text("\n".join(output_lines), encoding="utf-8")
