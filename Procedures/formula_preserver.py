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

def latex_to_unicode(s: str) -> str:
    return LatexNodes2Text(math_mode='text').latex_to_text(s)
