from Procedures import preserve_formulas
import re
from pylatexenc.latex2text import LatexNodes2Text

MASK_PREFIX = "⟦CEM:"
MASK_SUFFIX = "⟧"

def preserve_during_clean(text: str, cleaner, **kwargs):
    if not text:
        return ""
    
    formulas = preserve_formulas.extract_all_formulas(text)
    masked = text

    for i, f in enumerate(formulas):
        masked = re.sub(re.escape(f), f"{MASK_PREFIX}{i}{MASK_SUFFIX}", masked)

    cleaned = cleaner(masked, **kwargs)

    for i, f in enumerate(formulas):
        cleaned = cleaned.replace(f"{MASK_PREFIX}{i}{MASK_SUFFIX}", f)

    return cleaned

from pylatexenc.latex2text import LatexNodes2Text

def latex_to_unicode(text: str) -> str:
    pattern = preserve_formulas.LATEX_MATH_PATTERN
    conv = LatexNodes2Text(math_mode="text")

    def repl(m: re.Match) -> str:
        match_text = None
        for g in m.groups():
            if g:
                match_text = g
                break
        if match_text is None:
            return m.group(0)
        return conv.latex_to_text(match_text)

    return pattern.sub(repl, text)