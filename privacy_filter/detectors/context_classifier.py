"""
Context Classifier Module for FinTech Privacy Filter.

Performs intelligent context-aware disambiguation of numeric and ambiguous entities
(e.g., distinguishing Aadhaar vs Bank Account vs Loan Account for identical 12-digit strings)
by scanning surrounding multilingual context keywords across all official Indian languages.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from privacy_filter.detectors.regex_detector import Entity

# Comprehensive Multilingual Keyword Dictionaries for All 22 Official Scheduled Indian Languages
MULTILINGUAL_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "AADHAAR": {
        "en": ["aadhaar", "adhar", "uid", "uidai", "aadhar card", "uid card"],
        "hi": ["आधार", "आधार कार्ड", "यूआईडी"],
        "kn": ["ಆಧಾರ್", "ಆಧಾರ್ ಕಾರ್ಡ್", "ಯುಐಡಿ"],
        "ta": ["ஆதார்", "ஆதார் அட்டை", "யுஐடி"],
        "te": ["ఆధార్", "ఆధార్ కార్డ్", "యుఐడి"],
        "ml": ["ആധാർ", "ആധാർ കാർഡ്", "യുഐഡി"],
        "bn": ["আধার", "আধার কার্ড", "ইউআইডি"],
        "gu": ["આધાર", "આધાર કાર્ડ", "યુઆઈડી"],
        "mr": ["आधार", "आधार कार्ड", "यूआयडी"],
        "pa": ["ਆਧਾਰ", "ਆਧਾਰ ਕਾਰਡ"],
        "or": ["ଆଧାର", "ଆଧାର କାର୍ଡ"],
        "ur": ["آدھار", "آدھار کارڈ"],
        "as": ["আধাৰ", "আধাৰ কাৰ্ড"],
        "ks": ["آدھار"],
        "sd": ["آڌار"],
        "mai": ["आधार"],
        "mni": ["আধার"],
    },
    "LOAN_ACCOUNT": {
        "en": [
            "loan account", "loan no", "loan number", "loan id", "borrower", "lender", "sanction",
            "emi", "disbursement", "mortgage", "home loan", "personal loan", "loan"
        ],
        "hi": ["ऋण खाता", "ऋण संख्या", "ऋण", "कर्ज", "उधार"],
        "kn": ["ಸಾಲದ ಖಾತೆ", "ಸಾಲ ಸಂಖ್ಯೆ", "ಸಾಲ", "ಕಿರುಸಾಲ"],
        "ta": ["கடன் கணக்கு", "கடன் எண்", "கடன்"],
        "te": ["రుణ ఖాతా", "రుణ సంఖ్య", "రుణం", "అప్పు"],
        "ml": ["വായ്പാ അക്കൗണ്ട്", "വായ്പ നമ്പർ", "വായ്പ"],
        "bn": ["ঋণ অ্যাকাউন্ট", "ঋণ নম্বর", "ঋণ"],
        "gu": ["લોન ખાતું", "લોન નંબર", "લોન"],
        "mr": ["कर्ज खाते", "कर्ज क्रमांक", "कर्ज"],
        "pa": ["ਕਰਜ਼ਾ ਖਾਤਾ", "ਕਰਜ਼ਾ ਨੰਬਰ", "ਕਰਜ਼ਾ"],
        "or": ["ଋଣ ଖାତା", "ଋଣ ନମ୍ବର", "ଋଣ"],
        "ur": ["قرض اکاؤنٹ", "قرض نمبر", "قرض"],
    },
    "ACCOUNT_NUMBER": {
        "en": [
            "account number", "bank account", "account no", "ac no", "a/c", "acct no",
            "account", "acct", "savings account", "current account", "deposit account"
        ],
        "hi": ["खाता संख्या", "बैंक खाता", "खाता", "बचत खाता", "चालू खाता"],
        "kn": ["ಖಾತೆ ಸಂಖ್ಯೆ", "ಬ್ಯಾಂಕ್ ಖಾತೆ", "ಖಾತೆ", "ಉಳಿತಾಯ ಖಾತೆ"],
        "ta": ["கணக்கு எண்", "வங்கி கணக்கு", "கணக்கு", "சேமிப்பு கணக்கு"],
        "te": ["ఖాతా సంఖ్య", "బ్యాంక్ ఖాతా", "ఖాతా", "పొదుపు ఖాతా"],
        "ml": ["അക്കൗണ്ട് നമ്പർ", "ബാങ്ക് അക്കൗണ്ട്", "അക്കൗണ്ട്", "സമ്പാദ്യ അക്കൗണ്ട്"],
        "bn": ["হিসাব নম্বর", "ব্যাংক অ্যাকাউন্ট", "অ্যাকাউন্ট", "সঞ্চয়ী হিসাব"],
        "gu": ["ખાતા નંબર", "બેંક ખાતું", "ખાતું", "બચત ખાતું"],
        "mr": ["खाते क्रमांक", "बँक खाते", "खाते", "बचत खाते"],
        "pa": ["ਖਾਤਾ ਨੰਬਰ", "ਬੈਂਕ ਖਾਤਾ", "ਖਾਤਾ"],
        "or": ["ଖାତା ନମ୍ବର", "ବ୍ୟାଙ୍କ ଖାତା", "ଖାତା"],
        "ur": ["بینک اکاؤنٹ", "اکاؤنٹ نمبر", "اکاؤنٹ"],
        "as": ["বেংক একাউণ্ট", "একাউণ্ট নম্বৰ", "একাউণ্ট"],
    },
    "CHEQUE_NUMBER": {
        "en": ["cheque number", "cheque leaf", "cheque", "check", "chq"],
        "hi": ["चेक संख्या", "चेक", "चैक"],
        "kn": ["ಚೆಕ್ ಸಂಖ್ಯೆ", "ಚೆಕ್"],
        "ta": ["காசோலை எண்", "காசோலை"],
        "te": ["చెక్ సంఖ్య", "చెక్"],
        "ml": ["ചെക്ക് നമ്പർ", "ചെക്ക്"],
        "bn": ["চেক নম্বর", "চেক"],
        "gu": ["ચેક નંબર", "ચેક"],
        "mr": ["चेक क्रमांक", "चेक"],
        "pa": ["ਚੈੱਕ ਨੰਬਰ", "ਚੈੱਕ"],
        "or": ["ଚେକ୍ ନମ୍ବର", "ଚେକ୍"],
        "ur": ["چیک نمبر", "چیک"],
    },
    "OTP": {
        "en": ["otp", "one time password", "verification code", "auth code"],
        "hi": ["ओटीपी", "सत्यापन कोड"],
        "kn": ["ಒಟಿಪಿ", "ಪರಿಶೀಲನಾ ಕೋಡ್"],
        "ta": ["ஒடிபி", "சரிபார்ப்பு குறியீடு"],
        "te": ["ఓటీపీ", "పరిశీలన కోడ్"],
        "ml": ["ഒടിപി", "സ്ഥിരീകരണ കോഡ്"],
        "bn": ["ওটিপি", "যাচাইকরণ কোড"],
        "gu": ["ઓટીપી"],
        "mr": ["ओटीपी"],
        "pa": ["ਓਟੀਪੀ"],
        "or": ["ଓଟିପି"],
        "ur": ["او ٹی پی"],
    },
    "MPIN": {
        "en": ["mpin", "m-pin", "mobile pin"],
        "hi": ["एमपिन", "पिन"],
        "kn": ["ಎಂಪಿನ", "ಪಿನ್"],
        "ta": ["எம்பிண்", "பின்"],
        "te": ["ఎమ్‌పిన్", "పిన్"],
        "ml": ["എംപിൻ", "പിൻ"],
        "bn": ["এমপিন", "পিন"],
        "gu": ["એમપિન"],
        "mr": ["एमपिन"],
        "ur": ["ایم پن"],
    },
    "PAN": {
        "en": ["pan card", "permanent account number", "pan", "income tax"],
        "hi": ["पैन कार्ड", "पैन", "आयकर"],
        "kn": ["ಪ್ಯಾನ್ ಕಾರ್ಡ್", "ಪ್ಯಾನ್"],
        "ta": ["பான் கார்டு", "பான்"],
        "te": ["పాన్ కార్డ్", "పాన్"],
        "ml": ["പാൻ കാർഡ്", "പാൻ"],
        "bn": ["প্যান কার্ড", "প্যান"],
        "gu": ["પાન કાર્ડ", "પાન"],
        "mr": ["पॅन कार्ड", "पॅन"],
        "pa": ["ਪੈਨ ਕਾਰਡ", "ਪੈਨ"],
        "or": ["ପ୍ୟାନ କାର୍ଡ", "ପ୍ୟାନ"],
        "ur": ["پین کارڈ", "پین"],
    },
    "POLICY_NUMBER": {
        "en": ["policy number", "policy no", "policy", "insurance", "premium", "claim"],
        "hi": ["पॉलिसी संख्या", "पॉलिसी", "बीमा"],
        "kn": ["ಪಾಲಿಸಿ ಸಂಖ್ಯೆ", "ಪಾಲಿಸಿ", "ವಿಮೆ"],
        "ta": ["காப்பீட்டு எண்", "காப்பீடு"],
        "te": ["పాలసీ సంఖ్య", "పాలసీ", "బీమా"],
        "ml": ["പോളിസി നമ്പർ", "പോളിസി", "ഇൻഷുറൻസ്"],
        "bn": ["পলিসি নম্বর", "পলিসি", "বীমা"],
        "gu": ["પોલિસી નંબર", "પોલિસી", "બીમો"],
        "mr": ["पॉलिसी क्रमांक", "पॉलिसी", "विमा"],
        "pa": ["ਪਾਲਿਸੀ ਨੰਬਰ", "ਬੀਮਾ"],
        "or": ["ପଲିସି ନମ୍ବର", "ବୀମା"],
        "ur": ["پالیسی نمبر", "بیمہ"],
    },
    "MICR": {
        "en": ["micr code", "micr", "magnetic ink character recognition"],
        "hi": ["एमआईसीआर", "एमआईसीआर कोड"],
        "kn": ["ಎಂಐಸಿಆರ್", "ಎಂಐಸಿಆರ್ ಕೋಡ್"],
        "ta": ["எம்ஐசிஆர்", "எம்ஐசிஆர் குறியீடு"],
        "te": ["ఎంఐసిఆర్", "ఎంఐసిఆర్ కోడ్"],
        "ml": ["എംഐസിആർ", "എംഐസിആർ കോഡ്"],
        "bn": ["এমআইসিআর", "এমআইসিআর কোড"],
        "gu": ["એમઆઇસીઆર", "એમઆઇસીઆર કોડ"],
        "mr": ["एमआयसीआर", "एमआयसीआर कोड"],
        "pa": ["ਐਮਆਈਸੀਆਰ"],
        "or": ["ଏମଆଇସିଆର"],
        "ur": ["ایم آئی سی آر"],
    },
    "IFSC": {
        "en": ["ifsc code", "ifsc", "indian financial system code"],
        "hi": ["आईएफएससी", "आईएफएससी कोड"],
        "kn": ["ಐಎಫ್ಎಸ್ಸಿ", "ಐಎಫ್ಎಸ್ಸಿ ಕೋಡ್"],
    },
    "SWIFT": {
        "en": ["swift code", "swift", "bic code", "bic", "swift-bic"],
        "hi": ["स्विफ्ट", "स्विफ्ट कोड"],
    },
    "CARD": {
        "en": ["card number", "credit card", "debit card", "card no", "visa", "mastercard", "rupay", "amex"],
        "hi": ["कार्ड", "क्रेडिट कार्ड", "डेबिट कार्ड"],
    },
    "CVV": {
        "en": ["cvv", "cvc", "security code", "cvv2", "cvc2"],
        "hi": ["सीवीवी", "सुरक्षा कोड"],
    },
    "UPI": {
        "en": ["upi", "vpa", "upi id", "pay payment address"],
        "hi": ["यूपीआई", "यूपीआई आईडी"],
    },
}


class ContextClassifier:
    """Intelligent context classifier for resolving entity ambiguities based on surrounding text."""

    def __init__(
        self,
        window_size: int = 50,
        keyword_dict: Optional[Dict[str, Dict[str, List[str]]]] = None,
    ) -> None:
        """Initialize ContextClassifier.

        Args:
            window_size: Number of characters before and after entity to scan for context.
            keyword_dict: Custom multilingual keyword dictionary.
        """
        self.window_size = window_size
        self.keyword_dict = keyword_dict or MULTILINGUAL_KEYWORDS

        self._flat_keywords: Dict[str, List[str]] = {}
        self._build_flat_keyword_map()

    def _build_flat_keyword_map(self) -> None:
        """Flattens multilingual keyword definitions into lower-case search lists."""
        for target_type, lang_map in self.keyword_dict.items():
            flat_list: Set[str] = set()
            for lang_code, kw_list in lang_map.items():
                for kw in kw_list:
                    flat_list.add(kw.strip().lower())
            self._flat_keywords[target_type] = sorted(list(flat_list), key=len, reverse=True)

    def find_closest_keyword(
        self, entity: Entity, full_text: str, candidate_types: List[str]
    ) -> Optional[Tuple[str, int]]:
        """Finds candidate target type whose keyword has closest proximity from keyword end to entity."""
        start_idx = max(0, entity.start - self.window_size)
        end_idx = min(len(full_text), entity.end + self.window_size)
        context_segment = full_text[start_idx:end_idx].lower()
        entity_rel_pos = entity.start - start_idx

        best_target: Optional[str] = None
        min_distance = float("inf")
        longest_kw_len = 0

        for target_type in candidate_types:
            keywords = self._flat_keywords.get(target_type, [])
            for kw in keywords:
                pos = context_segment.find(kw)
                while pos != -1:
                    kw_end = pos + len(kw)
                    dist = abs(entity_rel_pos - kw_end) if entity_rel_pos >= kw_end else abs(pos - entity_rel_pos)

                    if dist < min_distance or (dist == min_distance and len(kw) > longest_kw_len):
                        min_distance = dist
                        best_target = target_type
                        longest_kw_len = len(kw)

                    pos = context_segment.find(kw, pos + 1)

        if best_target is not None and min_distance < self.window_size:
            return best_target, min_distance

        return None

    def classify_entity(self, entity: Entity, full_text: str) -> Entity:
        """Analyzes context surrounding entity using proximity scoring to resolve type ambiguity."""
        if not full_text or entity.start < 0:
            return entity

        cleaned_digits = "".join(c for c in entity.text if c.isdigit())

        # Disambiguation for 12-digit numeric sequences
        if len(cleaned_digits) == 12:
            match_res = self.find_closest_keyword(
                entity, full_text, ["AADHAAR", "LOAN_ACCOUNT", "ACCOUNT_NUMBER"]
            )
            if match_res:
                matched_type, _ = match_res
                conf = 1.0 if matched_type == "AADHAAR" else 0.95
                return Entity(
                    type=matched_type,
                    text=entity.text,
                    start=entity.start,
                    end=entity.end,
                    confidence=conf,
                    category="CONTEXT_DISAMBIGUATED",
                )

            # Isolated 12-digit number without any contextual indicators
            if entity.type in {"ACCOUNT_NUMBER", "AADHAAR", "MICR", "CVV"}:
                return Entity(
                    type="UNKNOWN_NUMERIC_ID",
                    text=entity.text,
                    start=entity.start,
                    end=entity.end,
                    confidence=0.50,
                    category="ISOLATED_NUMERIC",
                )

        # Disambiguation for 9-digit numeric sequences (MICR vs Account Number)
        elif len(cleaned_digits) == 9:
            match_res = self.find_closest_keyword(
                entity, full_text, ["MICR", "ACCOUNT_NUMBER"]
            )
            if match_res:
                matched_type, _ = match_res
                return Entity(
                    type=matched_type,
                    text=entity.text,
                    start=entity.start,
                    end=entity.end,
                    confidence=0.95,
                    category="CONTEXT_DISAMBIGUATED",
                )

        # Disambiguation for 6-digit numeric sequences (Cheque vs OTP vs MPIN)
        elif len(cleaned_digits) == 6:
            match_res = self.find_closest_keyword(
                entity, full_text, ["CHEQUE_NUMBER", "OTP", "MPIN"]
            )
            if match_res:
                matched_type, _ = match_res
                return Entity(
                    type=matched_type,
                    text=entity.text,
                    start=entity.start,
                    end=entity.end,
                    confidence=0.95,
                    category="CONTEXT_DISAMBIGUATED",
                )

        return entity

    def classify_all(self, entities: List[Entity], full_text: str) -> List[Entity]:
        """Disambiguates a list of candidate Entity objects against full document context."""
        return [self.classify_entity(e, full_text) for e in entities]
