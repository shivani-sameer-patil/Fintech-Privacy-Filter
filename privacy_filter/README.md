# 🛡️ Production FinTech Privacy Filter

A high-performance, modular preprocessing pipeline designed to detect, mask, and sanitize Personally Identifiable Information (PII) and sensitive financial data from documents before transmitting them to Large Language Models (LLMs) or third-party APIs.

This toolkit ensures compliance with data privacy regulations (such as GDPR, CCPA, and Indian DPDPA) by keeping sensitive financial details secure on-premise or within your trusted environment.

---

## 🔍 Example Input → Sanitized Output

### Raw Input Document (English)
> *"Dear Customer Shivani Patil, your PAN card ABCDE1234F and Aadhaar 2345 6789 0123 have been verified. A premium amount of Rs. 12,500/year has been debited from account 123456789012. Contact us at support@fintech.co.in or +91 9876543210. Card used: 4111 1111 1111 1111."*

### Sanitized Output (Ready for LLM Prompt)
> *"Dear Customer `[PERSON]`, your PAN card `[PAN]` and Aadhaar `[AADHAAR]` have been verified. A premium amount of `[AMOUNT]` has been debited from account `[BANK_ACCOUNT]`. Contact us at `[EMAIL]` or `[PHONE_NUMBER]`. Card used: `[CARD]`."*

---

## 🌟 Key Features
- **28 FinTech & PII Entity Types**: Full coverage for structured financial identifiers and personal details.
- **Multilingual Support**: Supports English and **12 major Indian languages** (Hindi, Kannada, Tamil, Telugu, Malayalam, Gujarati, Marathi, Bengali, Odia, Punjabi, Assamese, Urdu).
- **Indic Numeral Normalization**: Converts non-ASCII digit symbols across 12+ Indian scripts into ASCII numbers without modifying non-digit text.
- **Multi-Detector Ensemble**: Combines rule-based non-backtracking Regex, Microsoft Presidio NLP, spaCy NER, and multilingual Context Classification.
- **Intelligent Context Disambiguation**: Differentiates identical digit patterns (e.g. 12-digit strings) as `AADHAAR`, `BANK_ACCOUNT`, or `LOAN_ACCOUNT` using surrounding multilingual trigger keywords.
- **Span-Preserving Masking**: Replaces sensitive entities from the end of document backwards to guarantee zero character index shifting.
- **Production Web Studio (GUI)**: Built-in local web interface for uploading text files, selecting document templates, sanitizing, and reviewing visual tag highlights and audit reports.

---

## ⚙️ Architecture & Pipeline Flow

The privacy filter employs a modular 10-step hybrid detection pipeline:

Input
  ↓
Language Detection
  ↓
Indic Numeral Normalization
  ↓
Regex + Presidio + spaCy + Keywords
  ↓
Context Classification
  ↓
Entity Merge
  ↓
Masking
  ↓
Sanitized Output

### Pipeline Flow Explanation
- **Language Detection & Normalization**: The pipeline detects the input language and normalizes non-ASCII digit representations across 12+ Indian scripts into ASCII digits `0-9` to ensure uniform pattern matching.
- **Ensemble Detection**: High-performance regex patterns, Microsoft Presidio Analyzer, spaCy Named Entity Recognition models, and keyword triggers detect candidate PII entities in parallel.
- **Disambiguation & Merging**: Surrounding context words are evaluated to differentiate similar strings (e.g., distinguishing a 12-digit number as `AADHAAR` vs. `BANK_ACCOUNT`). Overlapping entity spans are resolved greedily using priority, confidence, and span length.
- **Span-Preserving Masking**: Replaces entities starting from the end of the text backwards to prevent index shifting.

---

## 📋 Supported PII & Financial Entities

The pipeline classifies and masks **28 sensitive entity types** grouped into five logical categories:

| Category | Entity Type | Mapped Placeholder | Description / Format |
| :--- | :--- | :--- | :--- |
| **Personal Identity** | `PERSON` | `[PERSON]` | Full name, first name, last name |
| | `EMAIL` | `[EMAIL]` | RFC 5322 compliant email addresses |
| | `PHONE` | `[PHONE_NUMBER]` | Indian mobile numbers (+91/0 prefix support) |
| | `PAN` | `[PAN]` | Permanent Account Number (10 alphanumeric digits) |
| | `AADHAAR` | `[AADHAAR]` | Aadhaar ID (12 digits with space/hyphen separators) |
| | `PASSPORT` | `[PASSPORT]` | Indian Passport format (1 letter + 7 digits) |
| | `VOTER_ID` | `[VOTER_ID]` | EPIC ID (3 letters + 7 digits) |
| | `DRIVING_LICENSE`| `[DRIVING_LICENSE]`| Indian Driving License format |
| | `DATE` | `[DATE]` | Standard calendar date configurations |
| **Financial & Banking** | `BANK_ACCOUNT` | `[BANK_ACCOUNT]` | Bank account numbers (9-18 digits) |
| | `CARD` | `[CARD]` | Visa, Mastercard, Amex, RuPay card numbers |
| | `IFSC` | `[IFSC]` | Indian Financial System Code (11 characters) |
| | `MICR` | `[MICR]` | 9-digit Magnetic Ink Character Recognition code |
| | `SWIFT` | `[SWIFT]` | SWIFT/BIC codes (8 or 11 characters) |
| | `CVV` | `[CVV]` | 3 or 4-digit card security codes |
| | `UPI` | `[UPI]` | Virtual Payment Address (VPA) format |
| | `AMOUNT` | `[AMOUNT]` | Monetary values with multilingual currency names & suffixes |
| | `CHEQUE_NUMBER`| `[CHEQUE_NUMBER]` | 6-digit cheque number sequence |
| **Loans & Tax Info** | `LOAN_ACCOUNT` | `[LOAN_ACCOUNT]` | Loan Account Numbers with context prefixes |
| | `POLICY_NUMBER` | `[POLICY_NUMBER]` | Insurance Policy Numbers |
| | `GST` | `[GST]` | Goods & Services Tax Identification Number (15 char) |
| | `CIN` | `[CIN]` | Corporate Identity Number (21 characters) |
| | `CRYPTO_WALLET` | `[CRYPTO_WALLET]` | EVM addresses, Legacy/Segwit Bitcoin wallets |
| **System Security** | `IP_ADDRESS` | `[IP_ADDRESS]` | IPv4 and IPv6 addresses |
| | `MAC_ADDRESS` | `[MAC_ADDRESS]` | 6-pair hexadecimal MAC addresses |
| | `DEVICE_ID` | `[DEVICE_ID]` | RFC 4122 UUID and DEV-prefixed device identifiers |
| | `USERNAME` | `[USERNAME]` | User login names or @handles |
| | `PASSWORD` | `[PASSWORD]` | Password strings matching assignment patterns |
| | `OTP` | `[OTP]` | 4-8 digit One-Time Passwords |
| | `MPIN` | `[MPIN]` | 4-6 digit Mobile Banking PINs |
| | `TRANSACTION_PIN`| `[TRANSACTION_PIN]`| 4-6 digit Financial Transaction PINs |

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Programming Language**| Python 3.10+ | Core pipeline logic, API endpoints, and runner |
| **Rule-Based Engine** | Python Standard Library `re` / `regex` | Fast, non-backtracking regular expression matching |
| **NLP PII Engine** | Microsoft Presidio Analyzer | Context-aware PII detection and identification |
| **Named Entity Recognition**| spaCy (Model: `en_core_web_lg`) | Pre-trained large NER model for people, locations, and organizations |
| **Language Detection** | `langdetect` & Unicode ranges | Detects English and 12 major Indian languages |
| **Numeral Normalizer** | C-speed translation mappings | Translates 12+ Indic script numbers into standard ASCII numbers |
| **Web Server (GUI)** | Python `http.server` | Lightweight local host controller serving UI assets |
| **Frontend UI** | Vanilla HTML5 / CSS3 / JavaScript | Responsive Dark-themed studio dashboard and visual tag highlights |

---

## ⚡ Performance Characteristics

- **Full Offline Processing**: All text processing, neural network inferences, and regex matches are performed locally. No document data is sent to external APIs during sanitization.
- **Span-Preserving Masking**: Replaces PII starting from the end of the text backwards. This ensures character indexes and offsets do not shift, preserving data alignment.
- **Strictly Modular Layout**: Add, remove, or customize regex patterns, models, and tag formats without modifying the core pipeline structure.
- **Unicode-Safe Matching**: Regex patterns use Unicode classes rather than ASCII bounds, allowing proper matching of Indian scripts.
- **Precision Disambiguation**: The context engine checks surrounding keyword indices, preventing false positives (e.g. matching general 9-digit integers as MICR codes).

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
│   ├── pipeline.py            # Module 10: Master 10-step pipeline
│   └── multilingual_keyword_detector.py # Optional: Keyword-based proximity classifier
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
│   ├── test_pipeline.py
│   └── test_multilingual_keyword_detector.py # Keyword detector test suite
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
│   ├── demo_module10.py
│   └── verify_all_indian_languages.py # Script verifying language models
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

The pipeline architecture is strictly modular to facilitate future expansion:
- **FastAPI Migration**: Upgrade the lightweight local `http.server` to a full FastAPI REST API with automatic Swagger documentation.
- **Dockerization**: Containerize the app using Docker to allow seamless on-premise microservice orchestration.
- **OCR Integration**: Embed Tesseract or EasyOCR to extract and sanitize scanned KYC images and forms.
- **Custom LLM Masking**: Inject an LLM-backed validator into `context_classifier.py` for advanced zero-shot domain disambiguation.
- **Cloud Deployment**: Add templates for deploying as a serverless API (e.g., AWS Lambda, Google Cloud Run) for horizontal scaling.
- **Streaming Pipeline**: Build a real-time streaming parser using WebSockets or Server-Sent Events (SSE) for sanitizing live chat and agent-customer dialogues.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🤝 Acknowledgements

- [Microsoft Presidio](https://github.com/microsoft/presidio) for providing the high-quality modular PII Analyzer.
- [spaCy](https://spacy.io/) by Explosion AI for the advanced NER models.
- The developers of the 12 Indian script numeral datasets.
