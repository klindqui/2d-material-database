import textwrap
from pathlib import Path
import fitz
from typing import Optional

def text_to_pdf(
        text: str,
        out_path: str,
        *,
        title: Optional[str] = None,
        page_size: str = "letter",
        margins: tuple[float, float, float, float] = (72, 72, 72, 72),
        fontname: str = "helv",
        fontsize: float = 11.0,
        line_height: float = 1.4,
        fontfile: Optional[str] = None,
):
    SIZES = {"letter": (612, 792), "a4": (595, 842)}
    page_w, page_h = SIZES.get(page_size.lower(), SIZES["letter"])
    ml, mt, mr, mb = margins
    content_w = page_w - ml - mr
    content_h = page_h - mt - mb

    # Rough wrap calculations
    avg_char_w = 0.5 * fontsize
    chars_per_line = max(20, int(content_w / avg_char_w))
    line_px = fontsize * line_height
    lines_per_page = max(5, int(content_h / line_px))

    # Wrap to lines
    lines = []
    for para in text.splitlines():
        if not para.strip():
            lines.append("")
        else:
            lines.extend(textwrap.wrap(para, width=chars_per_line))

    doc = fitz.open()
    def new_page():
        return doc.new_page(width=page_w, height=page_h), mt

    page, y = new_page()
    used = 0
    if title:
        page.insert_text((ml, y), title, fontname=fontname, fontsize=fontsize+3, fontfile=fontfile)
        y += (fontsize+3) * line_height
        used += 1

    for ln in lines:
        if used >= lines_per_page:
            page, y = new_page()
            used = 0
        page.insert_text((ml, y), ln, fontname=fontname, fontsize=fontsize, fontfile=fontfile)
        y += line_px
        used += 1

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    doc.close()