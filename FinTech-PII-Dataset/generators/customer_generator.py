import random

from person_generator import (
    generate_person,
    generate_phone,
    generate_date,
)

from financial_generator import (
    generate_pan,
    generate_aadhaar,
    generate_passport,
    generate_driving_license,
)

from banking_generator import (
    generate_bank_account,
    generate_ifsc,
)


EMAIL_DOMAINS = [
    "gmail.com",
    "outlook.com",
    "icloud.com",
    "yahoo.com",
    "proton.me"
]

UPI_BANKS = [
    "oksbi",
    "okhdfcbank",
    "ybl",
    "ibl",
    "axl"
]


def generate_customer():

    person = generate_person()["value"]

    first_name = person.split()[0].lower()

    last_name = person.split()[-1].lower()

    email = (
        f"{first_name}.{last_name}"
        f"{random.randint(10,999)}"
        f"@{random.choice(EMAIL_DOMAINS)}"
    )

    upi = (
        f"{first_name}"
        f"{random.randint(10,999)}"
        f"@{random.choice(UPI_BANKS)}"
    )

    return {

        "PERSON": person,

        "PHONE": generate_phone()["value"],

        "EMAIL": email,

        "DATE": generate_date()["value"],

        "PAN": generate_pan()["value"],

        "AADHAAR": generate_aadhaar()["value"],

        "PASSPORT": generate_passport()["value"],

        "DRIVING_LICENSE":
            generate_driving_license()["value"],

        "BANK_ACCOUNT":
            generate_bank_account()["value"],

        "IFSC":
            generate_ifsc()["value"],

        "UPI":
            upi,
    }