from Procedures import preserve_formulas
import re

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