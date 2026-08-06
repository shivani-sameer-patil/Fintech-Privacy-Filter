EN_TO_HI = str.maketrans(
    "0123456789",
    "०१२३४५६७८९"
)

EN_TO_KN = str.maketrans(
    "0123456789",
    "೦೧೨೩೪೫೬೭೮೯"
)


def localize_digits(text, language="english"):

    text = str(text)

    if language == "hindi":
        return text.translate(EN_TO_HI)

    elif language == "kannada":
        return text.translate(EN_TO_KN)

    return text