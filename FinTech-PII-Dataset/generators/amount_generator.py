import random


# English digits
ENGLISH_FORMATS = [
    "₹{}",
    "Rs. {}",
    "INR {}",
    "{} INR",
    "Rupees {}"
]


# Hindi labels
HINDI_FORMATS = [
    "₹{}",
    "रु. {}",
    "{} रुपये",
    "₹{} रुपये"
]


# Kannada labels
KANNADA_FORMATS = [
    "₹{}",
    "ರೂ. {}",
    "{} ರೂಪಾಯಿ",
    "₹{} ರೂಪಾಯಿ"
]


EN_TO_HI = str.maketrans(
    "0123456789",
    "०१२३४५६७८९"
)

EN_TO_KN = str.maketrans(
    "0123456789",
    "೦೧೨೩೪೫೬೭೮೯"
)


def indian_format(number):

    s = str(number)

    if len(s) <= 3:
        return s

    last3 = s[-3:]
    rest = s[:-3]

    parts = []

    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return ",".join(parts + [last3])


def generate_amount(language="english"):

    amount = random.randint(
        500,
        5000000
    )

    formatted = indian_format(amount)

    if language == "english":

        fmt = random.choice(ENGLISH_FORMATS)

        return {
            "value": fmt.format(formatted),
            "label": "AMOUNT"
        }

    elif language == "hindi":

        formatted = formatted.translate(EN_TO_HI)

        fmt = random.choice(HINDI_FORMATS)

        return {
            "value": fmt.format(formatted),
            "label": "AMOUNT"
        }

    elif language == "kannada":

        formatted = formatted.translate(EN_TO_KN)

        fmt = random.choice(KANNADA_FORMATS)

        return {
            "value": fmt.format(formatted),
            "label": "AMOUNT"
        }

    else:

        return {
            "value": formatted,
            "label": "AMOUNT"
        }


if __name__ == "__main__":

    print("English")
    for _ in range(5):
        print(generate_amount("english"))

    print()

    print("Hindi")
    for _ in range(5):
        print(generate_amount("hindi"))

    print()

    print("Kannada")
    for _ in range(5):
        print(generate_amount("kannada"))