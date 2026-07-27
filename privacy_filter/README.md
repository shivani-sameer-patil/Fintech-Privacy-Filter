# Production FinTech Privacy Filter

An intelligent preprocessing pipeline designed to detect and mask Personally Identifiable Information (PII) and sensitive financial data before documents are sent to Large Language Models (LLMs).

---

## 🌟 Key Features
- **28 FinTech & PII Entity Types**: PAN, Aadhaar, Passport, Voter ID, Driving License, Email, Phone, Card (Visa/MC/Amex/RuPay), Bank Account, IFSC, MICR, SWIFT, CVV, UPI, GSTIN, CIN, Loan Account, Policy Number, Cheque Number, Crypto Wallet, IP Address, MAC Address, Device ID, Username, Password, OTP, MPIN, Transaction PIN, Person, Organization, Location, Date.
- **Multilingual Support**: Supports English and all **12 Official Scheduled Indian Languages** (Hindi, Kannada, Tamil, Telugu, Malayalam, Gujarati, Marathi, Bengali, Odia, Punjabi, Assamese, Urdu).
- **Indic Numeral Normalization**: Converts non-ASCII digits across 12+ Indian scripts into ASCII numbers without modifying non-digit text.
- **Multi-Detector Ensemble**: Combines rule-based non-backtracking Regex, Microsoft Presidio, spaCy NER, and multilingual Context Classification.
- **Intelligent Context Disambiguation**: Distinguishes identical numeric patterns (e.g. 12-digit strings) as `AADHAAR`, `BANK_ACCOUNT`, or `LOAN_ACCOUNT` using surrounding multilingual trigger keywords.
- **Span-Preserving Masking**: Replaces sensitive entities from the end of document backwards to guarantee zero character index shifting.
- **Production Web Studio (GUI)**: Built-in local web interface for uploading text files, selecting document templates, sanitizing, and reviewing visual tag highlights and audit reports.

---

## 📁 Project Structure

```
privacy_filter/
│
├── app.py                     # Command-line & application entrypoint
├── config.py                  # Pipeline configuration parameters
├── requirements.txt           # Python dependencies
│
├── web/                       # Web Studio assets & local web server
│   ├── index.html             # Web Studio layout
│   ├── style.css              # Dark-theme styles
│   ├── script.js              # Interactive UI engine
│   └── server.py              # Lightweight HTTP handler & REST API
│
├── detectors/
│   ├── regex_patterns.py      # Module 1: Optimized regex registry
│   ├── regex_detector.py      # Module 2: Regex scanner with Luhn validation
│   ├── presidio_detector.py   # Module 3: Microsoft Presidio analyzer engine
│   ├── spacy_detector.py      # Module 4: spaCy NER detector
│   ├── language_detector.py   # Module 5: Multilingual language detector
│   ├── indic_normalizer.py    # Module 6: Indic numeral normalizer
│   ├── context_classifier.py  # Module 7: Context-aware disambiguator
│   ├── merger.py              # Module 8: Entity merger & overlap resolver
│   ├── masker.py              # Module 9: Text masker
│   └── pipeline.py            # Module 10: Master 10-step pipeline
│
├── tests/                     # Unit & integration test suite
│   ├── run_tests.py
│   ├── test_regex_patterns.py
│   ├── test_regex_detector.py
│   ├── test_presidio_detector.py
│   ├── test_spacy_detector.py
│   ├── test_language_detector.py
│   ├── test_indic_normalizer.py
│   ├── test_context_classifier.py
│   ├── test_merger.py
│   ├── test_masker.py
│   └── test_pipeline.py
│
├── samples/                   # Standalone module demonstration scripts
│   ├── demo_module1.py
│   ├── demo_module2.py
│   ├── demo_module3.py
│   ├── demo_module4.py
│   ├── demo_module5.py
│   ├── demo_module6.py
│   ├── demo_module7.py
│   ├── demo_module8.py
│   ├── demo_module9.py
│   └── demo_module10.py
│
└── README.md                  # Complete documentation
```

---

## 🚀 Quickstart

### 1. Installation
```bash
pip install -r privacy_filter/requirements.txt
```

### 2. Python API Usage
```python
from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline

# Initialize pipeline
pipeline = FinTechPrivacyPipeline()

# Input document
raw_document = """
Dear Customer Shivani Patil,
Your PAN card ABCDE1234F and Aadhaar 2345 6789 0123 have been verified.
Bank account 123456789012 with IFSC SBIN0001234. Card: 4111 1111 1111 1111.
Contact us at support@fintech.co.in or +91 9876543210.
"""

# Process document
output = pipeline.process(raw_document)

print("Sanitized Output:\n", output.masked_text)
print("Language Detected:", output.language.language_name)
print("Entities Masked:", output.entities_masked_count)
```

### 3. Launching Web Studio (GUI)
Run the lightweight web application server locally:
```bash
python privacy_filter/web/server.py
```
Open `http://localhost:8050` in Chrome/browser to interact with the responsive visual workspace. The Web Studio supports typing text, selecting pre-loaded multilingual document templates, uploading text-based logs and documents directly (e.g. `.txt`, `.json`, `.csv`, `.log`), and exporting sanitized outputs or JSON audit reports.

### 4. Command Line Execution
```bash
python privacy_filter/app.py --text "Contact Shivani Patil at shivani@gmail.com with PAN ABCDE1234F"
```

### 5. Running Unit Tests
```bash
python privacy_filter/tests/run_tests.py
```

---

## 🔮 Extensibility & Future Extensions
The pipeline architecture is strictly modular to support future extensions without breaking changes:
- **OCR Support**: Connect Tesseract / EasyOCR into `pipeline.py` step 1 for image-based scanned KYC forms.
- **Custom LLM Masking**: Inject an LLM-backed validator into `context_classifier.py` for advanced zero-shot domain disambiguation.
