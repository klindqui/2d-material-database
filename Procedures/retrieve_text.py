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
import clean_text

importlib.reload(report_class)
importlib.reload(database_class)
importlib.reload(clean_text)

def return_report(
        *,
        original_db: database_class.Database
) -> Optional[report_class.Report]:
    
    while True:
        doi = input("Enter DOI (enter to cancel): ").strip()
        if not doi:
            return
    
        if original_db.contains_doi(doi):
            report: report_class.Report = original_db.get(doi)
            return report
        else:
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


def extract_text_from_html(html_bytes: bytes, url: str = None) -> str:
    html_str = html_bytes.decode("utf-8", errors = "ignore")
    text = trafilatura.extract(html_str, include_links = False, include_formatting = False, url = url)
    return text or ""


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

    content = download_content(url)

    if content[:4] == b"%PDF":
        raw_text = extract_text_from_pdf(content)
    else:
        raw_text = extract_text_from_html(content, url)

    cleaned = clean_text.clean_text(
        raw_text,
        keep_only_sections = keep_only_sections,
        lowercase = False,
        ascii_only = False,
    )

    doi = getattr(report, "DOI", None)
    if doi and cleaned_db.contains_doi(doi):
        cleaned_report: report_class.Report = cleaned_db.get(doi)
        if hasattr(cleaned_report, "attach_text"):
            cleaned_report.attach_text(cleaned)
    else:
        pass
    
    return cleaned