import re
from chemdataextractor.doc import Document

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

    return sorted(alloys | cde_formulas)

# text = "Ti-6Al-4V and CuSO4·5H2O were analyzed. MoS2 has been doped with Fe"
# doc = Document(text)
# print([cem.text for cem in doc.cems])