"""
Regex Patterns Registry for FinTech Privacy Filter.

This module provides optimized, non-backtracking regular expressions for detecting
Personally Identifiable Information (PII) and financial sensitive data.

Categories:
- PERSONAL (Email, Phone, PAN, Aadhaar, Passport, Voter ID, Driving License)
- BANK (Account Number, IFSC, MICR, SWIFT, Credit/Debit Card, CVV, UPI)
- TAX_CORPORATE (GSTIN, CIN)
- FINANCIAL (Loan Account, Policy Number, Cheque Number, Crypto Wallet)
- SECURITY_SYSTEM (IP Address, MAC Address, Device ID, Username, Password, OTP, MPIN, Transaction PIN)
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Pattern, Optional


class EntityCategory(Enum):
    """Categories of sensitive entities."""
    PERSONAL = auto()
    BANK = auto()
    TAX_CORPORATE = auto()
    FINANCIAL = auto()
    SECURITY_SYSTEM = auto()


class EntityType(Enum):
    """Supported sensitive entity types."""
    # Personal
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    PAN = "PAN"
    AADHAAR = "AADHAAR"
    PASSPORT = "PASSPORT"
    VOTER_ID = "VOTER_ID"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    DATE = "DATE"

    # Bank
    ACCOUNT_NUMBER = "ACCOUNT_NUMBER"
    IFSC = "IFSC"
    MICR = "MICR"
    SWIFT = "SWIFT"
    CARD = "CARD"
    CVV = "CVV"
    UPI = "UPI"
    AMOUNT = "AMOUNT"

    # Tax & Corporate
    GST = "GST"
    CIN = "CIN"

    # Financial
    LOAN_ACCOUNT = "LOAN_ACCOUNT"
    POLICY_NUMBER = "POLICY_NUMBER"
    CHEQUE_NUMBER = "CHEQUE_NUMBER"
    CRYPTO_WALLET = "CRYPTO_WALLET"

    # Security & System
    IP_ADDRESS = "IP_ADDRESS"
    MAC_ADDRESS = "MAC_ADDRESS"
    DEVICE_ID = "DEVICE_ID"
    USERNAME = "USERNAME"
    PASSWORD = "PASSWORD"
    OTP = "OTP"
    MPIN = "MPIN"
    TRANSACTION_PIN = "TRANSACTION_PIN"


@dataclass(frozen=True)
class PatternDefinition:
    """Dataclass holding detailed pattern metadata and compiled regex object."""
    entity_type: EntityType
    category: EntityCategory
    compiled_regex: Pattern[str]
    raw_regex: str
    description: str
    examples: List[str] = field(default_factory=list)


class RegexPatternRegistry:
    """Central repository storing compiled regular expression definitions."""

    _PATTERNS: Dict[EntityType, PatternDefinition] = {}

    @classmethod
    def _register(
        cls,
        entity_type: EntityType,
        category: EntityCategory,
        raw_regex: str,
        description: str,
        examples: List[str],
        flags: int = re.VERBOSE | re.IGNORECASE,
    ) -> None:
        """Helper to compile and register a PatternDefinition."""
        compiled = re.compile(raw_regex, flags)
        cls._PATTERNS[entity_type] = PatternDefinition(
            entity_type=entity_type,
            category=category,
            compiled_regex=compiled,
            raw_regex=raw_regex,
            description=description,
            examples=examples,
        )

    @classmethod
    def get_pattern(cls, entity_type: EntityType) -> Optional[PatternDefinition]:
        """Retrieve a specific pattern definition by EntityType."""
        return cls._PATTERNS.get(entity_type)

    @classmethod
    def get_all_patterns(cls) -> Dict[EntityType, PatternDefinition]:
        """Retrieve all registered pattern definitions."""
        return dict(cls._PATTERNS)

    @classmethod
    def get_patterns_by_category(
        cls, category: EntityCategory
    ) -> List[PatternDefinition]:
        """Retrieve pattern definitions belonging to a specific Category."""
        return [
            p for p in cls._PATTERNS.values() if p.category == category
        ]


# =============================================================================
# PATTERN REGISTRATION & EXPLANATIONS
# =============================================================================

# EMAIL
RegexPatternRegistry._register(
    entity_type=EntityType.EMAIL,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        [A-Za-z0-9._%+-]+
        @
        [A-Za-z0-9.-]+
        \.
        [A-Za-z]{2,}
        \b
    """,
    description="RFC 5322 compliant standard email address regex with non-overlapping character classes.",
    examples=["shivani@gmail.com", "john.doe+test@fintech.co.in"],
)

# PHONE
RegexPatternRegistry._register(
    entity_type=EntityType.PHONE,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        (?:
            (?:\+91[\s\.-]?|0)
        )?
        [6-9]\d{4}
        [\s\.-]?
        \d{5}
        \b
    """,
    description="Indian mobile number matching 10-digit formats starting with 6-9, with optional +91/0 prefix.",
    examples=["+91 9876543210", "98765-43210", "09876543210", "9123456789"],
)

# PAN
RegexPatternRegistry._register(
    entity_type=EntityType.PAN,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        [A-Za-z]{3}
        [PCHFATBLJGEDIOpchfatbljgedio]
        [A-Za-z]
        \d{4}
        [A-Za-z]
        \b
    """,
    description="Indian Permanent Account Number (PAN) 10-character structure with 4th character entity type validation.",
    examples=["ABCDE1234F", "XYZPC9999Z", "FGHIJ5678K", "LMNOP1234Q"],
)

# AADHAAR
RegexPatternRegistry._register(
    entity_type=EntityType.AADHAAR,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        [1-9]\d{3}
        [\s-]?
        \d{4}
        [\s-]?
        \d{4}
        \b
    """,
    description="Indian 12-digit Aadhaar number with optional block separators.",
    examples=["234567890123", "9876-5432-1098", "1234 5678 9012"],
)

# PASSPORT
RegexPatternRegistry._register(
    entity_type=EntityType.PASSPORT,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        [A-Za-z]
        [1-9]\d{6}
        \b
    """,
    description="Indian Passport format: 1 letter series followed by 7 digits.",
    examples=["A1234567", "Z9876543"],
)

# VOTER ID
RegexPatternRegistry._register(
    entity_type=EntityType.VOTER_ID,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        [A-Za-z]{3}
        \d{7}
        \b
    """,
    description="Indian Voter ID (EPIC) format: 3 letters followed by 7 digits.",
    examples=["ABC1234567", "XYZ9876543"],
)

# DRIVING LICENSE
RegexPatternRegistry._register(
    entity_type=EntityType.DRIVING_LICENSE,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        [A-Za-z]{2}
        [-\s]?
        \d{2}
        [-\s]?
        (?:19|20)\d{2}
        [-\s]?
        \d{7}
        \b
    """,
    description="Indian Driving License format: State code (2L) + RTO (2D) + Year (4D) + Serial (7D).",
    examples=["MH-12-2011-0012345", "DL1420110012345", "KA 01 2020 1234567"],
)

# DATE
RegexPatternRegistry._register(
    entity_type=EntityType.DATE,
    category=EntityCategory.PERSONAL,
    raw_regex=r"""
        \b
        (?:
            \d{1,2}[-/\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/\s]\d{2,4}
            |
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}
            |
            \d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}
            |
            \d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}
        )
        \b
    """,
    description="Standard calendar date formats.",
    examples=["12 July 2026", "12/07/2026", "July 12, 2026", "2026-07-12"],
)

# ACCOUNT NUMBER
RegexPatternRegistry._register(
    entity_type=EntityType.ACCOUNT_NUMBER,
    category=EntityCategory.BANK,
    raw_regex=r"""
        \b
        \d{9,18}
        \b
    """,
    description="Bank Account Number matching 9 to 18 digits.",
    examples=["123456789012", "987654321012345"],
)

# IFSC
RegexPatternRegistry._register(
    entity_type=EntityType.IFSC,
    category=EntityCategory.BANK,
    raw_regex=r"""
        \b
        [A-Za-z]{4}
        0
        [A-Za-z0-9]{6}
        \b
    """,
    description="Indian Financial System Code (IFSC): 4 letters + '0' + 6 alphanumeric.",
    examples=["SBIN0001234", "HDFC0000240", "ICIC0000104"],
)

# MICR
RegexPatternRegistry._register(
    entity_type=EntityType.MICR,
    category=EntityCategory.BANK,
    raw_regex=r"""
        \b
        \d{9}
        \b
    """,
    description="9-digit MICR code (City + Bank + Branch).",
    examples=["400002015", "110002001"],
)

# SWIFT / BIC CODE
RegexPatternRegistry._register(
    entity_type=EntityType.SWIFT,
    category=EntityCategory.BANK,
    raw_regex=r"""
        \b
        [A-Z]{4}
        [A-Z]{2}
        [A-Z0-9]{2}
        (?:[A-Z0-9]{3})?
        \b
    """,
    description="SWIFT/BIC Code (8 or 11 uppercase characters) for international banking transactions.",
    examples=["SBININBBXXX", "HDFCINBB", "ICICINBB123"],
    flags=re.VERBOSE,  # Strict uppercase checking
)

# CREDIT / DEBIT CARD
RegexPatternRegistry._register(
    entity_type=EntityType.CARD,
    category=EntityCategory.BANK,
    raw_regex=r"""
        \b
        (?:
            4\d{3}
          | 5[1-5]\d{2} | 222[1-9] | 22[3-9]\d | 2[3-6]\d{2} | 27[01]\d | 2720
          | 3[47]\d{2}
          | 6011 | 65\d{2} | 60\d{2}
          | 508\d
        )
        [-\s]?
        \d{4}
        [-\s]?
        \d{4}
        [-\s]?
        \d{3,4}
        \b
    """,
    description="Payment card number matching Visa, Mastercard, Amex, and RuPay card formats.",
    examples=[
        "4111 1111 1111 1111",
        "5500-0000-0000-0004",
        "378282246310005",
        "6011111111111111",
    ],
)

# CVV
RegexPatternRegistry._register(
    entity_type=EntityType.CVV,
    category=EntityCategory.BANK,
    raw_regex=r"""
        \b
        (?:CVV|CVC|CVV2|CVC2|SECURITY\s+CODE|CVV\s+CODE|CVC\s+CODE)
        [:\s\.-]*
        \d{3,4}
        \b
    """,
    description="Card Verification Value (CVV/CVC) with explicit context indicator.",
    examples=["CVV: 123", "CVC 9876", "CVV2: 456"],
)

# AMOUNT
_boundary = r"(?<![^\s\.\,\!\?\(\)\[\]\{\}\-\:।])"
_boundary_end = r"(?![^\s\.\,\!\?\(\)\[\]\{\}\-\:।])"

_english_words = r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|hunderd|thousand|lakhs?|crores?|millions?|billions?|trillions?|zero)\b"

_indic_words = r"(?:एक|दो|तीन|चार|पाँच|पांच|छह|छतः|सात|आठ|नौ|दस|ग्यारह|बारह|तेरह|चौदह|पंद्रह|पन्द्रह|सोलह|सत्रह|अठारह|उन्नीस|बीस|इक्कीस|बाईस|तेईस|चौबीस|पच्चीस|छब्बीस|सत्ताईस|अठ्ठाईस|अट्ठाईस|उनतीस|उन्नतीस|तीस|इकतीस|बत्तीस|तैंतीस|तेतीस|चौंतीस|पैंतीस|छत्तीस|सैंतीस|अड़तीस|अढ़तीस|उनतालीस|उन्नतालीस|चालीस|इकतालीस|इकतालिस|बयालीस|तैंतालीस|तेतालीस|chiyalees|चौआलीस|पैंतालीस|छियालीस|सैंतालीस|अड़तालीस|अढ़तालीस|उनचाas|पचास|इक्यावन|बावन|तिरेपन|तिरपन|चौवन|पचपन|छप्पन|सत्तावन|अठ्ठावन|अट्ठावन|उनसठ|साठ|इकसठ|बासठ|तिरेसठ|तिरसठ|चौंसठ|पैंसठ|छियासठ|सरसठ|अड़सठ|अढ़सठ|उनहत्तर|सत्तर|इकहत्तर|बहत्तर|तिहत्तर|चौहत्तर|पचहत्तर|छिहत्तर|सतहत्तर|अठहत्तर|उन्यासी|उनासी|अस्सी|इक्यासी|बयासी|तिरासी|चौरासी|पचासी|छियासी|सत्तासी|अठ्यासी|अट्ठासी|नवासी|नब्बे|इक्यानवे|बानवे|तिर्यानवे|तिरानवे|चौरानवे|पञ्चानवे|पचानवे|छियानवे|सत्तानवे|अठ्यानवे|अट्ठानवे|निन्यानवे|सौ|हजार|हज़ार|लाख|करोड़|करोड़|सैकड़ा|दोन|पाच|सहा|नऊ|दहा|शंभर|कोटी|ಒಂದು|ಎರಡು|ಮೂರು|ನಾಲ್ಕು|ಐದು|ಆರು|ಏಳು|ಎಂಟು|ಒಂಬತ್ತು|ಹತ್ತು|ಇಪ್ಪತ್ತು|ಮೂವತ್ತು|ನಲವತ್ತು|ಐವತ್ತು|ಅರವತ್ತು|ಎಪ್ಪತ್ತು|ಎಂಭತ್ತು|ತೊಂಬತ್ತು|ನೂರು|ಸಾವಿರ|ಲಕ್ಷ|ಕೋಟಿ|ஒன்று|ஒன்னு|இரண்டு|ரெண்டு|மூன்று|மூணு|நான்கு|நாலு|ஐந்து|அஞ்சு|ஆறு|ஏழு|எட்டு|ஒன்பது|பத்து|இருபது|முப்பது|நாற்பது|ஐம்பது|அறுபது|எழுபது|எண்பது|தொண்ணூறு|நூறு|ஆயிரம்|லட்சம்|கோடி|ఒకటి|రెండు|మూడు|నాలుగు|ఐదు|ఆరు|ఏడు|ఎనిమిది|తొమ్మిది|పది|ఇరవై|ముప్పై|నలభై|యాభై|అరవై|డెబ్బై|ఎనభై|తొంభై|వంద|వేల|లక్ష|కోటి|ഒന്ന്|രണ്ട്|മൂന്ന്|നാല്|അഞ്ച്|ആറ്|ഏഴ്|എട്ട്|ഒമ്പത്|പത്ത്|ഇരുപത്|മുപ്പത്|നാൽപത്|അൻപത്|അറുപത്|എഴുപത്|എൺപത്|തൊണ്ണൂറ്|നൂറ്|ആയിരം|ലക്ഷം|കോടി|এক|দুই|তিন|চার|পাঁচ|ছয়|সাত|আট|নয়|দশ|বিশ|কুড়ি|ত্রিশ|চল্লিশ|পঞ্চাশ|ষাট|সত্তর|আশি|নব্বই|শত|হাজার|লাখ|লক্ষ|কোটি|એક|બે|ત્રણ|ચાર|પાંચ|છ|સાત|આઠ|નવ|દસ|વીસ|ત્રીસ|ચાલીસ|પચાસ|સાઇઠ|સિત્તેર|એસી|નેવું|સો|હજાર|લાખ|કરોડ|ਇੱਕ|ਦੋ|ਤਿੰਨ|ਚਾਰ|ਪੰਜ|ਛੇ|ਸੱਤ|ਅੱਠ|ਨੌ|ਦਸ|ਵੀਹ|ਤੀਹ|ਚਾਲੀ|ਪੰਜਾਹ|ਸੱਠ|ਸੱਤਰ|ਅੱਸੀ|ਨੱਬੇ|ਸੌ|ਹਜ਼ਾਰ|ਲੱਖ|ਕਰੋੜ)"

_digits = r"\b\d+(?:,\d+)*(?:\.\d+)?\b"

_num_words = rf"(?:{_english_words}|(?:{_boundary}{_indic_words}{_boundary_end})|{_digits})"

_seq = r"(?:" + _num_words + r"[\s\-\,]+(?:and[\s\-]+)?)*" + _num_words
_cur = r"(?:rupees?|rs\.?|inr|₹|रुपये|रूपये|रूपए|रुपए|रूपया|रुपया|रू|रु\.?|ರೂಪಾಯಿ|ರೂ\.?|ரூபாய்|ரூ\.?|രൂപ|ടাকা|રૂપિયા|ਰੁਪਏ|روپے|\$|€|£)"

RegexPatternRegistry._register(
    entity_type=EntityType.AMOUNT,
    category=EntityCategory.FINANCIAL,
    raw_regex=rf"{_boundary}(?:{_cur}\s*(?:{_seq})|(?:{_seq})\s*{_cur}){_boundary_end}",
    description="Monetary amount in Indian Rupees (INR) or major currencies, in numeric, comma-separated, or word formats.",
    examples=["Rs. 15,000", "₹ 15,000", "15,000 रुपये", "15,000.00 rupees", "$1,500", "Three thousand two hunderd twenty one rupees"],
    flags=re.IGNORECASE,
)

# UPI
RegexPatternRegistry._register(
    entity_type=EntityType.UPI,
    category=EntityCategory.BANK,
    raw_regex=r"""
        \b
        [a-zA-Z0-9._-]{2,64}
        @
        [a-zA-Z]{2,32}
        \b
    """,
    description="UPI Virtual Payment Address (VPA).",
    examples=["shivani@upi", "9876543210@ybl", "john.doe@okicici", "user@paytm"],
)

# GSTIN
RegexPatternRegistry._register(
    entity_type=EntityType.GST,
    category=EntityCategory.TAX_CORPORATE,
    raw_regex=r"""
        \b
        \d{2}
        [A-Za-z]{5}
        \d{4}
        [A-Za-z]
        [1-9A-Za-z]
        [Zz]
        [0-9A-Za-z]
        \b
    """,
    description="Indian Goods and Services Tax Identification Number (GSTIN) 15-character structure.",
    examples=["27ABCDE1234F1Z5", "07AAAAA0000A1Z5"],
)

# CIN
RegexPatternRegistry._register(
    entity_type=EntityType.CIN,
    category=EntityCategory.TAX_CORPORATE,
    raw_regex=r"""
        \b
        [ULul]
        \d{5}
        [A-Za-z]{2}
        (?:19|20)\d{2}
        [A-Za-z]{3}
        \d{6}
        \b
    """,
    description="Indian Corporate Identity Number (CIN) 21-character structure.",
    examples=["U72200MH2020PTC123456", "L15140GJ1991PLC016139"],
)

# LOAN ACCOUNT
RegexPatternRegistry._register(
    entity_type=EntityType.LOAN_ACCOUNT,
    category=EntityCategory.FINANCIAL,
    raw_regex=r"""
        \b
        (?:LAN|LN|LOAN)
        [-\s]?
        (?=[A-Z0-9-]*\d)
        [A-Z0-9-]{6,16}
        \b
    """,
    description="Loan Account Number with standard financial prefix indicators and uppercase alphanumeric ID.",
    examples=["LN-1234-567890", "LAN123456789012", "LOAN 987654321"],
    flags=re.VERBOSE,
)

# POLICY NUMBER
RegexPatternRegistry._register(
    entity_type=EntityType.POLICY_NUMBER,
    category=EntityCategory.FINANCIAL,
    raw_regex=r"""
        \b
        (?:POL|POLICY)
        [-\s]?
        (?=[A-Z0-9-]*\d)
        [A-Z0-9-]{6,16}
        \b
    """,
    description="Insurance Policy Number format with uppercase alphanumeric identifier.",
    examples=["POL123456789", "POLICY-98765432", "POL 0011223344"],
    flags=re.VERBOSE,
)

# CHEQUE NUMBER
RegexPatternRegistry._register(
    entity_type=EntityType.CHEQUE_NUMBER,
    category=EntityCategory.FINANCIAL,
    raw_regex=r"""
        \b
        \d{6}
        \b
    """,
    description="6-digit Indian Cheque Leaf Number.",
    examples=["000123", "654321"],
)

# CRYPTO WALLET
RegexPatternRegistry._register(
    entity_type=EntityType.CRYPTO_WALLET,
    category=EntityCategory.FINANCIAL,
    raw_regex=r"""
        \b
        (?:
            0x[a-fA-F0-9]{40}
          | [13][a-km-zA-HJ-NP-Z1-9]{25,34}
          | bc1[a-z0-9]{38,59}
        )
        \b
    """,
    description="Ethereum EVM and Bitcoin (Legacy, Segwit, Bech32) wallet address format.",
    examples=[
        "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
        "bc1qvqcf294yd03ycah56xly0n9xfzcd74nn29ydlj",
    ],
    flags=re.VERBOSE,
)

# IP ADDRESS
RegexPatternRegistry._register(
    entity_type=EntityType.IP_ADDRESS,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        \b
        (?:
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.
            (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)
          |
            (?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}
        )
        \b
    """,
    description="IPv4 and IPv6 network address format.",
    examples=["192.168.1.1", "10.0.0.255", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"],
)

# MAC ADDRESS
RegexPatternRegistry._register(
    entity_type=EntityType.MAC_ADDRESS,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        \b
        (?:[0-9a-fA-F]{2}[:-]){5}
        [0-9a-fA-F]{2}
        \b
    """,
    description="6-pair hexadecimal MAC address.",
    examples=["00:1A:2B:3C:4D:5E", "00-1A-2B-3C-4D-5E"],
)

# DEVICE ID
RegexPatternRegistry._register(
    entity_type=EntityType.DEVICE_ID,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        \b
        (?:
            [0-9a-fA-F]{8}-
            [0-9a-fA-F]{4}-
            [0-9a-fA-F]{4}-
            [0-9a-fA-F]{4}-
            [0-9a-fA-F]{12}
          |
            DEV-[0-9a-fA-F]{4,8}(?:-[0-9a-fA-F]{4,12})+
        )
        \b
    """,
    description="RFC 4122 UUID / Device ID format (8-4-4-4-12 hex chars or DEV- prefixed hex segments).",
    examples=["123e4567-e89b-12d3-a456-426614174000", "550e8400-e29b-41d4-a716-446655440000", "DEV-8f3a-99b1", "DEV-AB12-CD34-EF56"],
)

# USERNAME
RegexPatternRegistry._register(
    entity_type=EntityType.USERNAME,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        (?:
            \b(?:
                user|username|user_id|handle|trading_id|trading\s*id
              | उपयोगकर्ता\s*नाम|उपयोगकर्ता|यूज़रनेम
              | ব্যবহারকারীর\s*নাম|ব্যবহারকারী\s*নাম|ইউজারনেম
              | ಬಳಕೆದಾರಹೆಸರು|ಬಳಕೆದಾರ\s*ಹೆಸರು
              | பயனர்\s*பெயர்|பயனர்பெயர்
              | యూజర్‌నేమ్|వినియోగదారు\s*పేరు
              | ഉപയോക്തൃനാമം|ഉപയോക്തൃ\s*നാമം
              | વપરાશકર્તા\s*નામ|વપરાશકર્તાનામ
              | वापरकर्ता\s*नाव|वापरकर्तानाव|युझरनेम
              | ਉਪਭੋਗਤਾ\s*ਨਾਮ|ਉਪਭੋਗਤਾ\s*ਨਾਂ
              | ଉପଭୋକ୍ତା\s*ନାମ|ଉପଭୋକ୍ତାନାମ
              | صارف\s*نام|صارفنام
              | ব্যৱহাৰকাৰী\s*নাম|ব্যৱহাৰকাৰীৰ\s*নাম
              | صارف\s*ناو|صارف\s*نالو|वापरपी\s*नांव
              | शिजিনবরিবা\s*মিং|बाहागोআরि\s*মুং|ᱵᱮᱵᱷᱟᱨᱤᱭᱟᱹ\s*ᱧᱩᱛᱩ𝐦
              | प्रयोगकर्ता\s*नाम
            )\s*[:=]\s*([A-Za-z0-9_.-]{3,30})
          |
            (?:^|\s)@([A-Za-z0-9_]{3,30})\b
        )
    """,
    description="Username format matching key assignment syntax or @handle syntax.",
    examples=["username: john_doe99", "user = admin.sec", "@shivani_p", "उपयोगकर्ता नाम: admin_shivani", "trading_id: KAV45879"],
)

# PASSWORD
RegexPatternRegistry._register(
    entity_type=EntityType.PASSWORD,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        \b
        (?:
            password|passwd|pass|pwd|secret
          | पासवर्ड|क्रीटशब्द
          | পাসওয়ার্ড|পাসওয়ার্ড|গুপ্তশব্দ
          | ಪಾಸ್‌ವರ್ಡ್|ಗುಪ್ತಪದ
          | கடவுச்சொல்|கடவுச்சொற்கள்
          | పాస్‌వర్డ్|రహస్యపదం
          | പാസ്‌വേഡ്|പാസ്സ്‌വേർഡ്
          | પાસવર્ડ
          | पासवर्ड|गुप्तशब्द
          | ਪਾਸਵਰਡ
          | ପାସୱାର୍ଡ
          | پاس\s*ورڈ|پاسورڈ
          | পাছৱৰ্ড
          | ᱯᱟᱥᱣᱟᱨᱰ
          | पासवर्ड
        )\s*[:=]\s*
        (\S+)
    """,
    description="Password credential assignment syntax (password: secret).",
    examples=["password: SecretPass123!", "pwd = My#Secure99", "पासवर्ड: SecretP@ssw0rd2026!"],
)

# OTP
RegexPatternRegistry._register(
    entity_type=EntityType.OTP,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        \b
        (?:otp|one\s*time\s*pass(?:word|code)|verification\s*code)\s*[:=]?\s*
        (\d{4,8})
        \b
    """,
    description="4 to 8-digit One-Time Password (OTP) codes.",
    examples=["OTP: 482910", "verification code = 1234", "One Time Password 987654"],
)

# MPIN
RegexPatternRegistry._register(
    entity_type=EntityType.MPIN,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        \b
        (?:mpin|m-pin|mobile\s*pin)\s*[:=]?\s*
        (\d{4,6})
        \b
    """,
    description="4 or 6-digit Mobile Banking PIN (MPIN).",
    examples=["MPIN: 1234", "m-pin = 987654"],
)

# TRANSACTION PIN
RegexPatternRegistry._register(
    entity_type=EntityType.TRANSACTION_PIN,
    category=EntityCategory.SECURITY_SYSTEM,
    raw_regex=r"""
        \b
        (?:tx\s*pin|txn\s*pin|transaction\s*pin)\s*[:=]?\s*
        (\d{4,6})
        \b
    """,
    description="4 or 6-digit Financial Transaction PIN.",
    examples=["tx pin: 4321", "transaction pin = 654321"],
)
