import random

FIELD_VARIATIONS = {

    "CUSTOMER_NAME": [
        "Customer Name",
        "Applicant Name",
        "Full Name",
        "Name",
        "Account Holder",
        "Customer",
        "Primary Applicant",
        "Registered Name"
    ],

    "PHONE": [
        "Phone",
        "Phone Number",
        "Mobile",
        "Mobile Number",
        "Registered Mobile",
        "Contact Number",
        "Contact"
    ],

    "EMAIL": [
        "Email",
        "Email Address",
        "Registered Email",
        "Primary Email",
        "E-mail"
    ],

    "PAN": [
        "PAN",
        "PAN Number",
        "PAN Card",
        "Permanent Account Number",
        "PAN Card Number"
    ],

    "AADHAAR": [
        "Aadhaar",
        "Aadhaar Number",
        "UID",
        "UIDAI Number",
        "Unique ID"
    ],

    "ACCOUNT": [
        "Account",
        "Bank Account",
        "Savings Account",
        "Account Number",
        "Primary Account"
    ],

    "IFSC": [
        "IFSC",
        "IFSC Code",
        "Branch IFSC",
        "Bank IFSC"
    ],

    "UPI": [
        "UPI",
        "UPI ID",
        "UPI Handle",
        "UPI Address"
    ],

    "AMOUNT": [
        "Income",
        "Annual Income",
        "Declared Income",
        "Declared Annual Income",
        "Yearly Income"
    ]

}


def vary(text):

    for key, values in FIELD_VARIATIONS.items():

        text = text.replace(
            f"<<{key}>>",
            random.choice(values)
        )

    return text