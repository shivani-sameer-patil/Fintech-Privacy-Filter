# 🛡️ Production FinTech Privacy Filter

A high-performance, modular preprocessing pipeline designed to detect, mask, and sanitize Personally Identifiable Information (PII) and sensitive financial data from documents before transmitting them to Large Language Models (LLMs) or third-party APIs.

This toolkit ensures compliance with data privacy regulations (such as GDPR, CCPA, and Indian DPDPA) by keeping sensitive financial details secure on-premise or within your trusted environment.

---

## 🔍 Example Input → Sanitized Output

### Raw Input Document (English)
> *"Dear Customer Shivani Patil, your PAN card ABCDE1234F and Aadhaar 1234 5678 9012 have been verified. A premium amount of Rs. 12,500/year has been debited from account 123456789012. Contact us at support@fintech.co.in or +91 9876543210. Card used: 4111 1111 1111 1111."*

### Sanitized Output (Ready for LLM Prompt)
> *"Dear Customer `[PERSON]`, your PAN card `[PAN]` and Aadhaar `[AADHAAR]` have been verified. A premium amount of `[AMOUNT]` has been debited from account `[BANK_ACCOUNT]`. Contact us at `[EMAIL]` or `[PHONE_NUMBER]`. Card used: `[CARD]`."*

---

## 🌟 Key Features

- **Parallel NER Inferences**: Integrates a **fine-tuned GLiNER Large model** run in parallel with spaCy and Microsoft Presidio for highly accurate zero-shot entity extraction.
- **28 FinTech & PII Entity Types**: Full coverage for structured financial identifiers (Aadhaar, PAN, Card, IFSC, UPI) and personal details.
- **Multilingual Support**: Supports English and **12 major Indian languages** (Hindi, Kannada, Tamil, Telugu, Malayalam, Gujarati, Marathi, Bengali, Odia, Punjabi, Assamese, Urdu).
- **Indic Numeral Normalization**: Converts non-ASCII digit symbols across 12+ Indian scripts into standard ASCII numbers without modifying non-digit text.
- **Multi-Engine Telemetry Source Tracking**: The Web UI telemetry and audit logs track and display up to the top 2 contributing engines (e.g., `REGEX, GLINER` or `PRESIDIO, SPACY`) that detected the entity span.
- **Intelligent Context Disambiguation**: Differentiates identical digit patterns (e.g. 12-digit strings) as `AADHAAR`, `BANK_ACCOUNT`, or `LOAN_ACCOUNT` using surrounding multilingual trigger keywords.
- **Span-Preserving Masking**: Replaces sensitive entities from the end of document backwards to guarantee zero character index shifting.
- **Web Studio (GUI)**: Modern, responsive, local web interface powered by **FastAPI** to upload files, load multilingual templates, sanitize text, and view real-time latency telemetry and visual tag highlights.

---

## ⚙️ Architecture & Pipeline Flow

The privacy filter employs a modular 10-step hybrid detection pipeline:

```
           Input
            ↓
     Language Detection
            ↓
  Indic Numeral Normalization
            ↓
 ┌──────────────────────────────────────────────┐
 │               PARALLEL DETECT                │
 │  ┌──────────┐ ┌──────────┐ ┌───────┐ ┌─────┐ │
 │  │  Regex   │ │ Presidio │ │ spaCy │ │GLiNER│ │
 │  └──────────┘ └──────────┘ └───────┘ └─────┘ │
 └──────────────────────┬───────────────────────┘
                        ↓
             Context Classification
                        ↓
            Entity Merger & Resolver
                        ↓
                  Text Masking
                        ↓
               Sanitized Output
```

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
| **Rule-Based Engine** | Python `re` / `regex` | Fast, non-backtracking regular expression matching |
| **PII Analyzer** | Microsoft Presidio Analyzer | Context-aware PII detection and identification |
| **Fine-Tuned NER** | GLiNER Large | Deep-learning Named Entity Recognition for custom FinTech structures |
| **General NER** | spaCy (Model: `en_core_web_lg`) | Large pre-trained English model for Person names and dates |
| **API Backend** | FastAPI (with Uvicorn) | High-performance API server with OpenAPI (Swagger) |
| **Frontend UI** | HTML5 / CSS3 / JS | Dark-themed telemetry dashboard and visual tag highlights |

---

## 📁 Project Structure

```
privacy_filter/
├── app.py                      # Command-line application entrypoint
├── config.py                   # Pipeline configuration parameters
├── requirements.txt            # Python dependencies
│
├── web/                        # Web Studio static assets & backend
│   ├── index.html              # Web Studio interface
│   ├── style.css               # Dark-theme styles
│   ├── script.js               # Interactive UI engine (cache-busted)
│   └── server.py               # FastAPI static server & REST API
│
├── detectors/
│   ├── regex_patterns.py       # Optimized regex patterns
│   ├── regex_detector.py       # Regex scanner with Luhn check and Entity schema
│   ├── presidio_detector.py    # Microsoft Presidio analyzer wrapper
│   ├── spacy_detector.py       # spaCy NER detector
│   ├── gliner_detector.py      # GLiNER parallel PII extraction wrapper
│   ├── language_detector.py    # Unicode-range multilingual detector
│   ├── indic_normalizer.py     # Transliterates Indic scripts digits
│   ├── indic_number_words.py   # Large index of Indic number triggers
│   ├── context_classifier.py   # Context-aware proximity disambiguator
│   ├── merger.py               # Overlap resolution & engine sources merging
│   ├── masker.py               # Backwards span-preserving text masker
│   ├── finetuned_gliner/       # [Ignored] Fine-tuned model binary files (1.79 GB)
│   └── multilingual_keyword_detector.py # Keyword-based digit analyzer
│
├── evaluation/                 # Evaluation and training module
│   ├── evaluate.py             # Runs precision/recall/F1 metrics on jsonl test set
│   ├── train_gliner.py         # Script to fine-tune GLiNER on custom datasets
│   ├── evaluation_report.json  # Overall evaluation statistics
│   ├── entity_metrics.csv      # Metrics breakdown per entity type
│   ├── language_metrics.csv    # Metrics breakdown per language
│   └── error_analysis.csv      # Error audit log (MISS, FALSE_POSITIVE, WRONG_LABEL)
│
└── tests/                      # Unit & integration test suite
    ├── run_tests.py            # Test suite runner
    ├── test_gliner_detector.py # GLiNER detector unit tests
    └── ...                     # Sub-component tests
```

---

## 🚀 Usage & Quickstart

### 1. Installation
Install python dependencies and spaCy language pack:
```bash
pip install -r privacy_filter/requirements.txt
python -m spacy download en_core_web_lg
```

### 2. Python API Usage
```python
from privacy_filter.detectors.pipeline import FinTechPrivacyPipeline

# Initialize pipeline (loads GLiNER and spaCy models locally)
pipeline = FinTechPrivacyPipeline()

# Input document
raw_document = "Shivani Patil has Aadhaar 1234 5678 9012 and PAN ABCDE1234F."

# Process document
output = pipeline.process(raw_document)

print("Sanitized Output:\n", output.masked_text)
print("Language Detected:", output.language.language_name)
print("Entities Masked:", output.entities_masked_count)
```

### 3. Launching Web Studio (GUI)
Run the FastAPI web application server locally:
```bash
python -m privacy_filter.web.server
```
Open **`http://localhost:8050`** in your browser. The Web Studio supports entering text, selecting pre-loaded templates, uploading text files (`.txt`, `.json`, `.csv`, `.log`), and displaying real-time latency telemetry alongside contributing engines.

### 4. Running the Model Evaluation Module
To evaluate the current pipeline predictions against a gold-standard JSONL dataset:
```bash
python -m privacy_filter.evaluation.evaluate
```
This computes Precision, Recall, and F1 metrics, saving reports (`evaluation_report.json`, `entity_metrics.csv`, `language_metrics.csv`, `error_analysis.csv`) inside `privacy_filter/evaluation/`.

### 5. Running the Test Suite
Ensure all components are operating correctly:
```bash
python privacy_filter/tests/run_tests.py
```

---

## 🐳 Docker Deployment

To build and launch the FinTech Privacy Filter inside a Docker container:

1. **Build the image**:
   ```bash
   docker build -t fintech-privacy-filter .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8050:8050 fintech-privacy-filter
   ```
   Open `http://localhost:8050` to access the running service.

---

## 📄 License

This project is licensed under the MIT License.
