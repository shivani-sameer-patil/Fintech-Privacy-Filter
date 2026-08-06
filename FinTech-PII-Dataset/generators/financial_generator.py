import random
import string


# -----------------------------
# PAN
# Format: ABCDE1234F
# -----------------------------
def generate_pan():
    letters = "".join(random.choices(string.ascii_uppercase, k=5))
    digits = "".join(random.choices(string.digits, k=4))
    last = random.choice(string.ascii_uppercase)

    return {
        "value": f"{letters}{digits}{last}",
        "label": "PAN"
    }


# -----------------------------
# Aadhaar
# Format: XXXX XXXX XXXX
# -----------------------------
from number_converter import localize_digits

def generate_aadhaar(language="english"):

    aadhaar = " ".join(
        str(random.randint(1000, 9999))
        for _ in range(3)
    )

    aadhaar = localize_digits(
        aadhaar,
        language
    )

    return {
        "value": aadhaar,
        "label": "AADHAAR"
    }


# -----------------------------
# Passport
# Format: A1234567
# -----------------------------
def generate_passport():
    return {
        "value": random.choice(string.ascii_uppercase)
                 + "".join(random.choices(string.digits, k=7)),
        "label": "PASSPORT"
    }


# -----------------------------
# Voter ID
# Format: ABC1234567
# -----------------------------
def generate_voter_id():
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    digits = "".join(random.choices(string.digits, k=7))

    return {
        "value": letters + digits,
        "label": "VOTER_ID"
    }


# -----------------------------
# Driving Licence
# Example:
# KA0120210001234
# -----------------------------
STATES = [
    "KA",
    "MH",
    "DL",
    "TN",
    "AP",
    "TS",
    "KL",
    "WB",
    "RJ",
    "UP",
    "PB",
    "HR",
    "GJ"
]


def generate_driving_license():

    state = random.choice(STATES)

    rto = str(random.randint(1, 99)).zfill(2)

    year = random.randint(2015, 2026)

    number = str(random.randint(1, 9999999)).zfill(7)

    dl = f"{state}{rto}{year}{number}"

    return {
        "value": dl,
        "label": "DRIVING_LICENSE"
    }


# -----------------------------
# Generate all
# -----------------------------
def generate_financial_identity():

    return {
        "pan": generate_pan(),
        "aadhaar": generate_aadhaar(),
        "passport": generate_passport(),
        "voter_id": generate_voter_id(),
        "driving_license": generate_driving_license()
    }


if __name__ == "__main__":

    for k, v in generate_financial_identity().items():
        print(v)