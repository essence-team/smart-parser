import re


def get_first_sentence(text):
    # Регулярное выражение для поиска первого предложения
    match = re.match(r"(.+?[.!?])\s", text + " ")
    if match:
        return match.group(1)
    else:
        return text  # Если знаки препинания не найдены
