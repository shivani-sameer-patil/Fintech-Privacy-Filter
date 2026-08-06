from faker import Faker
import random

fake_en = Faker("en_IN")
fake_hi = Faker("hi_IN")

EMAIL_DOMAINS = [
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "icloud.com",
    "proton.me",
    "hotmail.com",
]


# -----------------------------
# PERSON
# -----------------------------
# -----------------------------
# PERSON
# -----------------------------
HINDI_FIRST_NAMES = [
    "राहुल","अमित","अर्जुन","आकाश","रोहन",
    "विक्रम","सार्थक","आदित्य","अभिषेक","मोहित",
    "प्रिया","पूजा","नेहा","श्रेया","अनन्या",
    "काव्या","मीरा","नंदिनी","स्नेहा","रितिका"
]

HINDI_LAST_NAMES = [
    "शर्मा","पाटिल","गुप्ता","राव","कुलकर्णी",
    "सिंह","वर्मा","जोशी","देसाई","रेड्डी",
    "शेट्टी","नायर","भट्ट","यादव","मिश्रा"
]


KANNADA_FIRST_NAMES = [
    "ರಾಹುಲ್","ಅಮಿತ್","ಅರ್ಜುನ್","ಆಕಾಶ್","ರೋಹನ್",
    "ವಿಕ್ರಂ","ಸಾರ್ಥಕ್","ಆದಿತ್ಯ","ಅಭಿಷೇಕ್","ಮೋಹಿತ್",
    "ಪ್ರಿಯಾ","ಪೂಜಾ","ನೇಹಾ","ಶ್ರೇಯಾ","ಅನನ್ಯಾ",
    "ಕಾವ್ಯಾ","ಮೀರಾ","ನಂದಿನಿ","ಸ್ನೇಹಾ","ರಿತಿಕಾ"
]

KANNADA_LAST_NAMES = [
    "ಶರ್ಮಾ","ಪಾಟೀಲ್","ಗುಪ್ತಾ","ರಾವ್","ಕುಲಕರ್ಣಿ",
    "ಸಿಂಗ್","ವರ್ಮಾ","ಜೋಶಿ","ದೇಸಾಯಿ","ರೆಡ್ಡಿ",
    "ಶೆಟ್ಟಿ","ನಾಯರ್","ಭಟ್","ಯಾದವ್","ಮಿಶ್ರಾ"
]


def generate_person(language="english"):

    if language == "english":

        name = fake_en.name()

    elif language == "hindi":

        name = (
            random.choice(HINDI_FIRST_NAMES)
            + " "
            + random.choice(HINDI_LAST_NAMES)
        )

    elif language == "kannada":

        name = (
            random.choice(KANNADA_FIRST_NAMES)
            + " "
            + random.choice(KANNADA_LAST_NAMES)
        )

    else:

        name = fake_en.name()

    return {
        "value": name,
        "label": "PERSON"
    }


# -----------------------------
# PHONE
# -----------------------------
# -----------------------------
# PHONE
# -----------------------------
EN_TO_HI = str.maketrans(
    "0123456789",
    "०१२३४५६७८९"
)

EN_TO_KN = str.maketrans(
    "0123456789",
    "೦೧೨೩೪೫೬೭೮೯"
)


def generate_phone(language="english"):

    phone = str(
        random.randint(
            6000000000,
            9999999999
        )
    )

    if language == "hindi":

        phone = phone.translate(EN_TO_HI)
        phone = "+९१ " + phone

    elif language == "kannada":

        phone = phone.translate(EN_TO_KN)
        phone = "+೯೧ " + phone

    else:

        phone = "+91 " + phone

    return {
        "value": phone,
        "label": "PHONE"
    }
# -----------------------------
# EMAIL
# -----------------------------
def generate_email(language="english"):

    first = fake_en.first_name().lower()
    last = fake_en.last_name().lower()

    username = (
        first
        + "."
        + last
        + str(random.randint(1, 999))
    )

    email = username + "@" + random.choice(EMAIL_DOMAINS)

    return {
        "value": email,
        "label": "EMAIL",
    }

# -----------------------------
# DATE
# -----------------------------
DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%d %b %Y",
    "%d %B %Y",
]


def generate_date():

    d = fake.date_between(
        start_date="-70y",
        end_date="-18y"
    )

    fmt = random.choice(DATE_FORMATS)

    return {
        "value": d.strftime(fmt),
        "label": "DATE",
    }# -----------------------------
# DATE
# -----------------------------
# -----------------------------
# DATE
# -----------------------------
EN_DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%d %b %Y",
    "%d %B %Y",
]

HI_DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d %B %Y",
]

KN_DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d %B %Y",
]


HI_MONTHS_FULL = {
    "January": "जनवरी",
    "February": "फ़रवरी",
    "March": "मार्च",
    "April": "अप्रैल",
    "May": "मई",
    "June": "जून",
    "July": "जुलाई",
    "August": "अगस्त",
    "September": "सितंबर",
    "October": "अक्टूबर",
    "November": "नवंबर",
    "December": "दिसंबर",
}

HI_MONTHS_SHORT = {
    "Jan": "जन॰",
    "Feb": "फ़र॰",
    "Mar": "मार्च",
    "Apr": "अप्रैल",
    "May": "मई",
    "Jun": "जून",
    "Jul": "जुलाई",
    "Aug": "अगस्त",
    "Sep": "सित॰",
    "Oct": "अक्टू॰",
    "Nov": "नव॰",
    "Dec": "दिस॰",
}


KN_MONTHS_FULL = {
    "January": "ಜನವರಿ",
    "February": "ಫೆಬ್ರವರಿ",
    "March": "ಮಾರ್ಚ್",
    "April": "ಏಪ್ರಿಲ್",
    "May": "ಮೇ",
    "June": "ಜೂನ್",
    "July": "ಜುಲೈ",
    "August": "ಆಗಸ್ಟ್",
    "September": "ಸೆಪ್ಟೆಂಬರ್",
    "October": "ಅಕ್ಟೋಬರ್",
    "November": "ನವೆಂಬರ್",
    "December": "ಡಿಸೆಂಬರ್",
}

KN_MONTHS_SHORT = {
    "Jan": "ಜನ",
    "Feb": "ಫೆಬ್ರ",
    "Mar": "ಮಾರ್ಚ್",
    "Apr": "ಏಪ್ರಿಲ್",
    "May": "ಮೇ",
    "Jun": "ಜೂನ್",
    "Jul": "ಜುಲೈ",
    "Aug": "ಆಗಸ್ಟ್",
    "Sep": "ಸೆಪ್ಟೆಂ",
    "Oct": "ಅಕ್ಟೋ",
    "Nov": "ನವೆಂ",
    "Dec": "ಡಿಸೆಂ",
}


EN_TO_HI = str.maketrans(
    "0123456789",
    "०१२३४५६७८९"
)

EN_TO_KN = str.maketrans(
    "0123456789",
    "೦೧೨೩೪೫೬೭೮೯"
)


def generate_date(language="english"):

    d = fake_en.date_between(
        start_date="-70y",
        end_date="-18y"
    )

    if language == "english":

        fmt = random.choice(EN_DATE_FORMATS)

        return {
            "value": d.strftime(fmt),
            "label": "DATE"
        }

    elif language == "hindi":

        fmt = random.choice(HI_DATE_FORMATS)

        value = d.strftime(fmt)

        # Replace full month names first
        for en, hi in HI_MONTHS_FULL.items():
            value = value.replace(en, hi)

        # Replace abbreviated month names
        for en, hi in HI_MONTHS_SHORT.items():
            value = value.replace(en, hi)

        value = value.translate(EN_TO_HI)

        return {
            "value": value,
            "label": "DATE"
        }

    elif language == "kannada":

        fmt = random.choice(KN_DATE_FORMATS)

        value = d.strftime(fmt)

        for en, kn in KN_MONTHS_FULL.items():
            value = value.replace(en, kn)

        for en, kn in KN_MONTHS_SHORT.items():
            value = value.replace(en, kn)

        value = value.translate(EN_TO_KN)

        return {
            "value": value,
            "label": "DATE"
        }

    else:

        return {
            "value": d.strftime("%d/%m/%Y"),
            "label": "DATE"
        }


# -----------------------------
# GENDER
# -----------------------------
def generate_gender(language="english"):

    if language == "english":

        value = random.choice(
            [
                "Male",
                "Female"
            ]
        )

    elif language == "hindi":

        value = random.choice(
            [
                "पुरुष",
                "महिला"
            ]
        )

    elif language == "kannada":

        value = random.choice(
            [
                "ಪುರುಷ",
                "ಮಹಿಳೆ"
            ]
        )

    return {
        "value": value,
        "label": "GENDER"
    }

# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":

    print("English")
    for _ in range(5):
        print(generate_date("english"))

    print()

    print("Hindi")
    for _ in range(5):
        print(generate_date("hindi"))

    print()

    print("Kannada")
    for _ in range(5):
        print(generate_date("kannada"))