import locale
from datetime import datetime

month_mapping = {
    'Januar': 1, 'Februar': 2, 'März': 3, 'April': 4, 'Mai': 5, 'Juni': 6,
    'Juli': 7, 'August': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Dezember': 12
}

locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')


def date_parsing_from_word_str(date_str: str) -> datetime.date:
    if date_str is None or not isinstance(date_str, str) or date_str == "":
        return None
    parse_str = date_str.strip()
    try:
        if "März" in parse_str:
            day, month_str, year = parse_str.replace(".", "").split()
            geburtsjahr = datetime(int(year), month_mapping[month_str], int(day)).date()
        else:
            format_str = "%d. %B %y" if len(parse_str.split()[2]) == 2 else "%d. %B %Y"
            geburtsjahr = datetime.strptime(parse_str, format_str).date()
    except ValueError:
        raise ValueError(f"Could not parse date {date_str}. Unknown format.")
    return geburtsjahr


def date_parsing_from_iso_str(date_string: str) -> datetime.date:
    if date_string is None or not isinstance(date_string, str) or date_string == "":
        return None
    count_dash = date_string.count("-")
    if count_dash == 1:
        return datetime.strptime(date_string, "%Y-%m").date()
    elif count_dash == 2:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    else:
        raise ValueError("Could not parse date. Unknown format. Format is not ISO")


def date_parsing_from_str(date_string: str, iso: bool = False, word: bool = False) -> datetime.date:
    """
    Parse a date from a string. The string can have the following formats:
    - dd/mm/yyyy
    - mm/yyyy
    - dd.mm.yyyy
    - mm.yyyy
    - dd-mm-yyyy
    - mm-yyyy
    If the string is empty or none, None is returned.
    If the date is not valid then a ValueError is raised.
    :param word: if True, the date is parsed from a string with the format dd. month yy(yy)
    :type word: str
    :param iso: If True, the date is parsed from a string with the format yyyy-mm(-dd)
    :type iso: str
    :param date_string: string to parse
    :type date_string: str
    :return: date object
    :rtype:  datetime.date
    """
    if date_string is None or not isinstance(date_string, str):
        return None
    count_slash = date_string.count("/")
    count_point = date_string.count(".")
    count_dash = date_string.count("-")
    parse_str = date_string.strip().replace(" ", "")
    if parse_str == "":
        return None
    elif iso:
        return date_parsing_from_iso_str(parse_str)
    elif word:
        return date_parsing_from_word_str(parse_str)
    elif count_slash == 1:
        format_str = "%m/%y" if len(parse_str.split("/")[1]) == 2 else "%m/%Y"
    elif count_slash == 2:
        format_str = "%d/%m/%y" if len(parse_str.split("/")[2]) == 2 else "%d/%m/%Y"
    elif count_point == 1:
        format_str = "%m.%y" if len(parse_str.split(".")[1]) == 2 else "%m.%Y"
    elif count_point == 2:
        format_str = "%d.%m.%y" if len(parse_str.split(".")[2]) == 2 else "%d.%m.%Y"
    elif count_dash == 1:
        format_str = "%m-%y" if len(parse_str.split("-")[1]) == 2 else "%m-%Y"
    elif count_dash == 2:
        format_str = "%d-%m-%y" if len(parse_str.split("-")[2]) == 2 else "%d-%m-%Y"
    else:
        raise ValueError("Could not parse date. Unknown format")
    return datetime.strptime(parse_str, format_str).date()
