import re
from chemdataextractor.doc import Document

LATEX_MATH_PATTERN = re.compile(
    r"(\\\(.+?\\\))"          # \( ... \)
    r"|"
    r"(\\\[.+?\\\])"          # \[ ... \]
    r"|"
    r"(\$\$.+?\$\$)"          # $$ ... $$
    r"|"
    r"(\$[^$]+\$)",           # $ ... $
    re.DOTALL,
)

def extract_all_formulas(text: str):
    # use chemDataExtractor for standard chemicals
    cde_formulas = {cem.text for cem in Document(text).cems}

    # regex for alloy-style or hyphenated metals
    alloy_pattern = r'\b[A-Z][a-z]?(?:[-–]\d*[A-Z][a-z]?\d*)+\b'

    # regex for chained or hydrated chemical formulas
    # formula_pattern = r'(?:[A-Z][a-z]?\d*)+(?:·\d*(?:[A-Z][a-z]?\d*)+)?'

    # combine all results into one unique set
    alloys = set(re.findall(alloy_pattern, text))
    # chains = set(re.findall(formula_pattern, text))

    latex_formulas = {m.group(0) for m in LATEX_MATH_PATTERN.finditer(text)}

    return sorted(alloys | cde_formulas| latex_formulas )
