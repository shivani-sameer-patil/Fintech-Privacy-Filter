import random
import string

# -----------------------------
# APPLICATION ID
# Example: APP2026001234
# -----------------------------
def generate_application_id():

    year = random.randint(2023, 2027)
    number = random.randint(100000, 999999)

    return {
        "value": f"APP{year}{number}",
        "label": "APPLICATION_ID"
    }


# -----------------------------
# CUSTOMER ID
# Example: CUST483921
# -----------------------------
def generate_customer_id():

    number = random.randint(100000, 999999)

    return {
        "value": f"CUST{number}",
        "label": "CUSTOMER_ID"
    }


# -----------------------------
# LOAN ACCOUNT
# Example: LN000987654321
# -----------------------------
def generate_loan_account():

    number = "".join(random.choices(string.digits, k=12))

    return {
        "value": f"LN{number}",
        "label": "LOAN_ACCOUNT"
    }


# -----------------------------
# LOAN AMOUNT
# -----------------------------
def generate_loan_amount():

    amount = random.randrange(
        50000,
        5000000,
        5000
    )

    return {
        "value": f"₹{amount:,}",
        "label": "LOAN_AMOUNT"
    }


# -----------------------------
# EMI
# -----------------------------
def generate_emi():

    emi = random.randrange(
        1000,
        100000,
        500
    )

    return {
        "value": f"₹{emi:,}",
        "label": "EMI"
    }


# -----------------------------
# INTEREST RATE
# -----------------------------
def generate_interest_rate():

    rate = round(
        random.uniform(7.0, 18.5),
        2
    )

    return {
        "value": f"{rate}%",
        "label": "INTEREST_RATE"
    }


# -----------------------------
# TENURE
# -----------------------------
def generate_tenure():

    months = random.choice(
        [
            12,
            24,
            36,
            48,
            60,
            84,
            120,
            180,
            240
        ]
    )

    return {
        "value": f"{months} Months",
        "label": "TENURE"
    }


# -----------------------------
# EMPLOYER
# -----------------------------

EMPLOYERS = [
    "Infosys Ltd",
    "TCS",
    "Wipro",
    "Accenture",
    "IBM",
    "Google India",
    "Microsoft India",
    "Amazon",
    "HCL Technologies",
    "Tech Mahindra",
    "Capgemini",
    "Cognizant"
]


def generate_employer():

    return {
        "value": random.choice(EMPLOYERS),
        "label": "EMPLOYER"
    }


# -----------------------------
# DESIGNATION
# -----------------------------

DESIGNATIONS = [
    "Software Engineer",
    "Senior Software Engineer",
    "Data Scientist",
    "AI Engineer",
    "Project Manager",
    "Business Analyst",
    "HR Executive",
    "Accountant",
    "Professor",
    "Doctor"
]


def generate_designation():

    return {
        "value": random.choice(DESIGNATIONS),
        "label": "DESIGNATION"
    }


# -----------------------------
# SALARY
# -----------------------------
def generate_salary():

    salary = random.randrange(
        25000,
        300000,
        5000
    )

    return {
        "value": f"₹{salary:,}",
        "label": "SALARY"
    }


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":

    print(generate_application_id())
    print(generate_customer_id())
    print(generate_loan_account())
    print(generate_loan_amount())
    print(generate_emi())
    print(generate_interest_rate())
    print(generate_tenure())
    print(generate_employer())
    print(generate_designation())
    print(generate_salary())