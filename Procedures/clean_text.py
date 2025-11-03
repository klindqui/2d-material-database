import re
import unicodedata
from typing import Iterable, Tuple, Optional, List
from collections import Counter


def normalize_unicode(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = (s
         .replace("\u00A0", " ")  
         .replace("\ufb01", "fi")  
         .replace("\ufb02", "fl")
    )
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = s.replace("–", "-").replace("—", "-")
    return s

def join_hyphenated_linebreaks(s: str) -> str:
    return re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)

def strip_headers_footers(s: str) -> str:
    pages = re.split(r"\n{2,}", s)

    if len(pages) < 3:
        return s
    
    first_lines = []
    last_lines = []

    for p in pages:
        lines = [x.strip() for x in p.splitlines() if x.strip()]
        if not lines:
            continue
        first_lines.append(lines[0])
        last_lines.append(lines[-1])

    def frequent(items: Iterable[str], min_count: int) -> set:
        c = Counter(items)
        threshold = max(3, int(0.3 * len(pages)))
        return {k for k, v in c.items() if v >= threshold and len(k) <= 120}

    drop_first = frequent(first_lines, 3)
    drop_last = frequent(last_lines, 3)

    cleaned_pages: List[str] = []
    for p in pages:
        lines = [x.rstrip() for x in p.splitlines()]
        if lines and lines[0].strip() in drop_first:
            lines = lines[1:]
        if lines and lines[-1].strip() in drop_last:
            lines = lines[:-1]
        cleaned_pages.append("\n".join(lines))

    return "\n\n".join(cleaned_pages)

def remove_inline_numeric_citations(s: str) -> str:
    s = re.sub(r"\[(?:\d{1,3}(?:\s*[\-,–]\s*\d{1,3})?(?:\s*,\s*\d{1,3})*)\]", "", s)
    return s


def remove_parenthetical_citations(s: str) -> str:
    s = re.sub(r"\(([A-Z][A-Za-z\-]+(?:\s*&\s*[A-Z][A-Za-z\-]+)?(?:,\s*\d{4})(?:;\s*[A-Z][A-Za-z\-]+(?:,\s*\d{4}))*)\)", "", s)
    return s


def remove_figure_table_mentions(s: str) -> str:
    s = re.sub(r"\((?:Fig(?:ure)?|Table|Eq)\.?\s*\d+[a-z]?\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"(?:Fig(?:ure)?|Table|Eq)\.?\s*\d+[a-z]?", "", s, flags=re.IGNORECASE)
    return s


def remove_urls_emails(s: str) -> str:
    s = re.sub(r"\bhttps?://\S+\b", "", s)
    s = re.sub(r"\bwww\.\S+\b", "", s)
    s = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "", s)
    return s


def drop_sections(s: str, section_titles: Iterable[str]) -> str:
    pattern = r"|".join([re.escape(t) for t in section_titles])
    m = re.search(rf"(?mi)^\s*(?:\d+\.\s*)?(?:{pattern})\s*$", s)
    if m:
        return s[:m.start()].rstrip()
    return s

def dedupe_lines(s: str) -> str:
    seen = set()
    out = []
    for line in s.splitlines():
        key = line.strip()
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        out.append(line)
    return "\n".join(out)


def normalize_whitespace(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def keep_only_important_sections(s: str, keep: Tuple[str, ...] = ("Abstract", "Introduction")) -> str:
    titles = list(keep)
    boundaries = [re.compile(rf"(?mi)^\s*(?:\d+\.\s*)?{re.escape(t)}\s*$") for t in titles]

    segments = []
    for i, pat in enumerate(boundaries):
        m = pat.search(s)
        if not m:
            continue
        start = m.end()
        end = None
        for j in range(i + 1, len(boundaries)):
            m2 = boundaries[j].search(s, pos=start)
            if m2:
                end = m2.start()
                break
        seg = s[start:end].strip() if end else s[start:].strip()
        segments.append(f"{titles[i]}\n\n{seg}")

    return "\n\n\n".join(segments) if segments else s


def clean_text(
    raw: str,
    *,
    drop_headers_footers: bool = True,
    join_hyphens: bool = True,
    remove_numeric_citations: bool = True,
    remove_author_year_citations: bool = True,
    remove_fig_table_eq: bool = True,
    remove_urls_and_emails: bool = True,
    drop_from_sections: Tuple[str, ...] = ("References", "Acknowledgements", "Supplementary", "Supplementary Information"),
    keep_only_sections: Optional[Tuple[str, ...]] = None,
    lowercase: bool = False,
    ascii_only: bool = False,
    dedupe: bool = True,
) -> str:
   
    if not raw:
        return ""

    s = normalize_unicode(raw)
    if drop_headers_footers:
        s = strip_headers_footers(s)
    if join_hyphens:
        s = join_hyphenated_linebreaks(s)
    if remove_numeric_citations:
        s = remove_inline_numeric_citations(s)
    if remove_author_year_citations:
        s = remove_parenthetical_citations(s)
    if remove_fig_table_eq:
        s = remove_figure_table_mentions(s)
    if remove_urls_and_emails:
        s = remove_urls_emails(s)

    if keep_only_sections:
        s = keep_only_important_sections(s, keep_only_sections)

    if drop_from_sections:
        s = drop_sections(s, drop_from_sections)

    if dedupe:
        s = dedupe_lines(s)
    s = normalize_whitespace(s)

    if lowercase:
        s = s.lower()

    if ascii_only:
        s = s.encode("ascii", "ignore").decode("ascii", "ignore")

    return s
