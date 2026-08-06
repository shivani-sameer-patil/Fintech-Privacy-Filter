"""
Central registry for all entity generators.
"""

import re

PLACEHOLDER_PATTERN = r"\{([A-Z_]+)\}"


# -----------------------------
# Person Generators
# -----------------------------
from person_generator import (
    generate_person,
    generate_phone,
    generate_email,
    generate_date,
    generate_gender,
)


# -----------------------------
# Amount Generator
# -----------------------------
from amount_generator import (
    generate_amount,
)


# -----------------------------
# Financial Generators
# -----------------------------
from financial_generator import (
    generate_pan,
    generate_aadhaar,
    generate_passport,
    generate_voter_id,
    generate_driving_license,
)


# -----------------------------
# Banking Generators
# -----------------------------
from banking_generator import (
    generate_bank_account,
    generate_ifsc,
    generate_upi,
    generate_card,
    generate_cvv,
    generate_micr,
    generate_cheque_number,
)


# -----------------------------
# Loan Generators
# -----------------------------
from loan_generator import (
    generate_application_id,
    generate_customer_id,
    generate_loan_account,
    generate_loan_amount,
    generate_emi,
    generate_interest_rate,
    generate_tenure,
    generate_employer,
    generate_designation,
    generate_salary,
)


# =====================================================
# ENTITY REGISTRY
# =====================================================

ENTITY_GENERATORS = {

    # --------------------------------
    # Person
    # --------------------------------
    "PERSON": generate_person,
    "PHONE": generate_phone,
    "EMAIL": generate_email,
    "DATE": generate_date,
    "GENDER": generate_gender,

    # --------------------------------
    # Financial
    # --------------------------------
    "PAN": generate_pan,
    "AADHAAR": generate_aadhaar,
    "PASSPORT": generate_passport,
    "VOTER_ID": generate_voter_id,
    "DRIVING_LICENSE": generate_driving_license,

    # --------------------------------
    # Banking
    # --------------------------------
    "BANK_ACCOUNT": generate_bank_account,
    "IFSC": generate_ifsc,
    "UPI": generate_upi,
    "CARD": generate_card,
    "CVV": generate_cvv,
    "MICR": generate_micr,
    "CHEQUE_NUMBER": generate_cheque_number,

    # --------------------------------
    # Money
    # --------------------------------
    "AMOUNT": generate_amount,

    # --------------------------------
    # Loan
    # --------------------------------
    "APPLICATION_ID": generate_application_id,
    "CUSTOMER_ID": generate_customer_id,
    "LOAN_ACCOUNT": generate_loan_account,
    "LOAN_AMOUNT": generate_loan_amount,
    "EMI": generate_emi,
    "INTEREST_RATE": generate_interest_rate,
    "TENURE": generate_tenure,
    "EMPLOYER": generate_employer,
    "DESIGNATION": generate_designation,
    "SALARY": generate_salary,
}