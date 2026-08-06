import random
import string
from number_converter import localize_digits

# -----------------------------
# BANK ACCOUNT
# 9–18 digits
# -----------------------------
def generate_bank_account(language="english"):

    account = str(
        random.randint(
            1000000000,
            999999999999999999
        )
    )

    account = localize_digits(
        account,
        language
    )

    return {
        "value": account,
        "label": "BANK_ACCOUNT"
    }


# -----------------------------
# IFSC
# Example: SBIN0001234
# -----------------------------

BANK_CODES = [
    "SBIN",
    "HDFC",
    "ICIC",
    "UTIB",
    "PUNB",
    "BARB",
    "CNRB",
    "IDIB",
    "KKBK",
    "YESB"
]


def generate_ifsc():

    bank = random.choice(BANK_CODES)

    branch = str(random.randint(0, 9999)).zfill(4)

    return {
        "value": f"{bank}0{branch}",
        "label": "IFSC"
    }


# -----------------------------
# UPI
# -----------------------------

UPI_HANDLES = [
    "oksbi",
    "okhdfcbank",
    "okaxis",
    "ybl",
    "ibl",
    "paytm",
    "apl"
]


FIRST_NAMES = [
    "rahul",
    "amit",
    "neha",
    "ananya",
    "vivek",
    "riya",
    "fatima",
    "deepak",
    "sneha",
    "rohan"
]


def generate_upi():

    user = random.choice(FIRST_NAMES)

    if random.random() < 0.5:
        user += str(random.randint(1, 999))

    handle = random.choice(UPI_HANDLES)

    return {
        "value": f"{user}@{handle}",
        "label": "UPI"
    }


# -----------------------------
# CARD NUMBER (Luhn Valid)
# -----------------------------


def luhn_checksum(number):

    digits = [int(d) for d in number]

    odd = digits[-1::-2]

    even = digits[-2::-2]

    checksum = sum(odd)

    for d in even:
        checksum += sum(divmod(d * 2, 10))

    return checksum % 10


def generate_card(language="english"):

    prefix = "4"          # Visa

    body = "".join(random.choices(string.digits, k=14))

    partial = prefix + body

    for check in range(10):

        candidate = partial + str(check)

        if luhn_checksum(candidate) == 0:
            candidate = " ".join(
                [
                    candidate[i:i+4]
                    for i in range(0, 16, 4)
                ]
            )
            # Localize only the digits
            candidate = localize_digits(
                candidate,
                language
            )

            return {
                "value": candidate,
                "label": "CARD"
            }


# -----------------------------
# CVV
# -----------------------------

def generate_cvv():

    return {
        "value": str(random.randint(100, 999)),
        "label": "CVV"
    }


# -----------------------------
# MICR
# -----------------------------

def generate_micr():

    return {
        "value": "".join(random.choices(string.digits, k=9)),
        "label": "MICR"
    }


# -----------------------------
# CHEQUE NUMBER
# -----------------------------

def generate_cheque_number(language="english"):

    cheque = str(
        random.randint(
            100000,
            999999
        )
    )

    cheque = localize_digits(
        cheque,
        language
    )

    return {
        "value": cheque,
        "label": "CHEQUE_NUMBER"
    }


# -----------------------------
# ALL
# -----------------------------

def generate_banking():

    return {

        "account": generate_bank_account(),

        "ifsc": generate_ifsc(),

        "upi": generate_upi(),

        "card": generate_card(),

        "cvv": generate_cvv(),

        "micr": generate_micr(),

        "cheque": generate_cheque_number()

    }


if __name__ == "__main__":

    for k, v in generate_banking().items():
        print(v)