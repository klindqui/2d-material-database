# Procedures/retrieve_text.py
import importlib
import re
from pathlib import Path
from typing import Optional, Tuple

import requests

try:
    import trafilatura
except ImportError:
    raise ImportError("Please install trafilatura: pip install trafilatura")

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError("Please install PyMuPDF: pip install pymupdf")

from Classes import database_class, report_class
from Procedures import clean_text, formula_preserver, to_txt

importlib.reload(report_class)
importlib.reload(database_class)
importlib.reload(clean_text)
importlib.reload(formula_preserver)
importlib.reload(to_txt)


# ----------------------------
# Small utilities
# ----------------------------

def _safe_filename_from_doi(doi: str, max_len: int = 180) -> str:
    """
    Make a stable, filesystem-safe name from a DOI.
    """
    s = (doi or "").strip()
    s = s.replace("/", "_")
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")
    return s[:max_len] if s else "unknown_doi"


# ----------------------------
# Pick report by DOI
# ----------------------------

def return_report(*, original_db: database_class.Database) -> Optional[report_class.Report]:
    while True:
        doi = input("Enter DOI (enter to cancel): ").strip()
        if not doi:
            return None

        if original_db.contains_doi(doi):
            return original_db.get(doi)

        print(f"This database, {original_db.name}, does not contain the DOI {doi}")


# ----------------------------
# Download + extract text
# ----------------------------

def download_content(url: str) -> bytes:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; PaperTextBot/1.0)"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.content


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    parts = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            parts.append(page.get_text("text"))
    return "\n".join(parts)


def extract_text_from_html(html_bytes: bytes, url: Optional[str] = None) -> str:
    html_str = html_bytes.decode("utf-8", errors="ignore")
    text = trafilatura.extract(
        html_str,
        include_links=False,
        include_formatting=False,
        url=url,
    )
    return text or ""


def extract_raw_text(url: str) -> str:
    data = download_content(url)
    if data[:4] == b"%PDF":
        return extract_text_from_pdf(data)
    return extract_text_from_html(data, url)


# ----------------------------
# Store ONLY a reference in cleaned_db
# ----------------------------

def upsert_cleaned_report_text_ref(
    *,
    cleaned_db: database_class.Database,
    source_report: report_class.Report,
    text_ref: str,  # path to the .txt file
) -> None:
    doi = source_report.DOI

    if cleaned_db.contains_doi(doi):
        target: report_class.Report = cleaned_db.get(doi)
        target.attach_text(text_ref)
        print(f"Updated cleaned report ref for {doi} in {cleaned_db.name}")
        return

    new_rep = report_class.Report(
        DOI=source_report.DOI,
        title=source_report.title,
        link=source_report.link,
        notes=source_report.notes,
        text=None,
    )
    new_rep.attach_text(text_ref)
    cleaned_db.add_report(new_rep)
    print(f"Added new cleaned report ref for {doi} to {cleaned_db.name}")


# ----------------------------
# Main pipeline: fetch -> clean -> save txt -> store ref
# ----------------------------

def get_paper_text(
    *,
    original_db: database_class.Database,
    cleaned_db: database_class.Database,
    keep_only_sections: Optional[Tuple[str, ...]] = None,
    cleaned_txt_dir: str = "Cleaned_TXT",
    also_write_sidecar_json: bool = False,
) -> str:
    """
    Old behavior (BAD): stored full cleaned text in cleaned_db.
    New behavior (GOOD): writes Cleaned_TXT/<doi>.txt and stores that path in cleaned_db.
    Returns cleaned text so you can print/check it.
    """
    report = return_report(original_db=original_db)
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
        keep_only_sections=keep_only_sections,
        lowercase=False,
        ascii_only=False,
    )

    # Convert LaTeX → Unicode for readability in the .txt
    cleaned_for_txt = formula_preserver.latex_to_unicode(cleaned)

    # Save into Cleaned_TXT/
    out_dir = Path(cleaned_txt_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe = _safe_filename_from_doi(report.DOI)
    txt_path = out_dir / f"{safe}.txt"

    to_txt.write_paged_text_file(
        cleaned_for_txt,
        txt_path,
        title=report.title or "My Cleaned Paper",
    )

    # Store BOTH: a clickable GitHub link (text_ref) + also keep raw link in notes
    repo = "klindqui/2d-material-database"
    branch = "main"

    rel_path = txt_path.as_posix().replace("\\", "/")
    blob_url = f"https://github.com/{repo}/blob/{branch}/{rel_path}"
    raw_url  = f"https://raw.githubusercontent.com/{repo}/{branch}/{rel_path}"

    # Put the clickable "view" link in the DB text field
    upsert_cleaned_report_text_ref(
        cleaned_db=cleaned_db,
        source_report=report,
        text_ref=blob_url,
    )

    # OPTIONAL but recommended:
    # also store the raw link somewhere you can see it (notes is simplest)
    # if your Report.notes is used for other things, we can make a dedicated field later.
    try:
        if cleaned_db.contains_doi(report.DOI):
            r = cleaned_db.get(report.DOI)
            existing = (r.notes or "")
            extra = f"\nRAW_TEXT_URL: {raw_url}\nREL_TXT_PATH: {rel_path}"
            r.notes = (existing + extra).strip()
    except Exception:
        pass


    # Optional small JSON sidecar that points to the txt
    if also_write_sidecar_json:
        sidecar_path = out_dir / f"{safe}.json"
        to_txt.write_json_with_text_file_ref(
            txt_path=txt_path,
            json_out_path=sidecar_path,
            extra_fields={"doi": report.DOI, "title": report.title},
            include_hash=True,
            include_preview=False,
        )

    return cleaned
