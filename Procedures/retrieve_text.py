import importlib
import requests
from typing import Tuple, Optional

try:
    import trafilatura
except ImportError:
    raise ImportError("Please install trafilatura: pip install trafilatura")

try:
    import fitz
except ImportError:
    raise ImportError("Please install PyMuPDF: pip install pymupdf")

from Classes import database_class, report_class
from Procedures import clean_text, formula_preserver
from Procedures.formula_preserver import latex_to_unicode


importlib.reload(report_class)
importlib.reload(database_class)
importlib.reload(clean_text)
importlib.reload(formula_preserver)

def return_report(
        *,
        original_db: database_class.Database
) -> Optional[report_class.Report]:
    
    while True:
        doi = input("Enter DOI (enter to cancel): ").strip()
        if not doi:
            return None
    
        if original_db.contains_doi(doi):
            report: report_class.Report = original_db.get(doi)
            return report
        print(f"This database, {original_db.name}, does not contain the DOI {doi}")


def download_content(url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PaperTextBot/1.0)"
    }

    r = requests.get(url, headers = headers, timeout = 30)
    r.raise_for_status()
    return r.content


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    text_parts = []
    with fitz.open(
        stream = pdf_bytes,
        filetype = "pdf"
    ) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts)


def extract_text_from_html(html_bytes: bytes, url: Optional[str] = None) -> str:
    html_str = html_bytes.decode("utf-8", errors = "ignore")
    text = trafilatura.extract(html_str, include_links = False, include_formatting = False, url = url)
    return text or ""

def extract_raw_text(url: str) -> str:
    data = download_content(url)
    if data[:4] == b"%PDF":
        return extract_text_from_pdf(data)
    return extract_text_from_html(data, url)

def upsert_cleaned_db_entry(
        *,
        cleaned_db: database_class.Database,
        source_report: report_class.Report,
        cleaned_text: str
) -> None:
    doi = source_report.DOI
    if cleaned_db.contains_doi(doi):
        target: report_class.Report = cleaned_db.get(doi)
        target.attach_text(cleaned_text)
        print(f"Updated cleaned report for {doi} in {cleaned_db.name}")
    else:
        new_rep = report_class.Report(
            DOI = source_report.DOI,
            title = source_report.title,
            link = source_report.link,
            notes = source_report.notes,
            text = None
        )

        new_rep.attach_text(cleaned_text)
        cleaned_db.add_report(new_rep)
        print(f"Added new cleaned report for {doi} to {cleaned_db.name}")


def get_paper_text(
        *, 
        original_db: database_class.Database,
        cleaned_db: database_class.Database,
        keep_only_sections: Optional[Tuple[str, ...]] = None
) -> str:
    report = return_report(original_db = original_db)
    if report is None:
        return ""
    
    url = getattr(report, "link", None)
    if not url:
        print("Selected report has no link/URL")
        return ""
    
    raw_text = extract_raw_text(url)

    cleaned = formula_preserver.preserve_during_clean(
        raw_text,
        clean_text.clean_text,
        keep_only_sections = keep_only_sections,
        lowercase = False,
        ascii_only = False,
    )

    cleaned = latex_to_unicode(cleaned)

    upsert_cleaned_db_entry(
        cleaned_db = cleaned_db,
        source_report = report,
        cleaned_text = cleaned
    )

    return cleaned