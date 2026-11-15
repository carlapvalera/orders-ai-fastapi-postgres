import re


COUNTRY_ALIASES = {
    "spain": "España",
    "españa": "España",
    "espana": "España",
    "spanish market": "España",
    "france": "Francia",
    "francia": "Francia",
    "germany": "Alemania",
    "alemania": "Alemania",
    "italy": "Italia",
    "italia": "Italia",
    "portugal": "Portugal",
}

MONTH_ALIASES = {
    "january": "01", "enero": "01",
    "february": "02", "febrero": "02",
    "march": "03", "marzo": "03",
    "april": "04", "abril": "04",
    "may": "05", "mayo": "05",
    "june": "06", "junio": "06",
    "july": "07", "julio": "07",
    "august": "08", "agosto": "08",
    "september": "09", "septiembre": "09",
    "october": "10", "octubre": "10",
    "november": "11", "noviembre": "11",
    "december": "12", "diciembre": "12",
}


def _replace_aliases(question: str, aliases: dict[str, str], replacement_template: str = "{}") -> str:
    ordered = sorted(aliases, key=len, reverse=True)
    pattern = r"(?<!\w)(?:" + "|".join(re.escape(alias) for alias in ordered) + r")(?!\w)"
    return re.sub(
        pattern,
        lambda match: replacement_template.format(aliases[match.group(0).lower()]),
        question,
        flags=re.IGNORECASE,
    )


def normalize_question(question: str) -> str:
    """Normalize multilingual country and month aliases to canonical query terms."""
    normalized = _replace_aliases(question, COUNTRY_ALIASES)
    return _replace_aliases(normalized, MONTH_ALIASES, "month={}")

