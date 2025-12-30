# Procedures/to_txt.py
from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path
from typing import Optional


def write_paged_text_file(
    text: str,
    out_path: str | Path,
    *,
    title: Optional[str] = None,
    page_size: str = "letter",
    margins: tuple[float, float, float, float] = (72, 72, 72, 72),
    fontsize: float = 11.0,
    line_height: float = 1.4,
    page_break: str = "\n\n\f\n\n",
    encoding: str = "utf-8",
) -> Path:
    """
    Writes a readable .txt with soft page breaks (form-feed) similar to your PDF paging logic.
    """
    SIZES = {"letter": (612, 792), "a4": (595, 842)}
    page_w, page_h = SIZES.get(page_size.lower(), SIZES["letter"])
    ml, mt, mr, mb = margins

    content_w = page_w - ml - mr
    content_h = page_h - mt - mb

    avg_char_width = 0.5 * fontsize
    chars_per_line = max(20, int(content_w / avg_char_width))

    line_px = fontsize * line_height
    lines_per_page = max(5, int(content_h / line_px))

    wrapped_lines: list[str] = []
    for para in (text or "").splitlines():
        if not para.strip():
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(textwrap.wrap(para, width=chars_per_line))

    output: list[str] = []
    used = 0

    if title:
        output.append(title)
        output.append("")
        used += 2

    for line in wrapped_lines:
        if used >= lines_per_page:
            output.append(page_break.rstrip("\n"))
            used = 0
        output.append(line)
        used += 1

    out_path_p = Path(out_path)
    out_path_p.parent.mkdir(parents=True, exist_ok=True)
    out_path_p.write_text("\n".join(output).rstrip() + "\n", encoding=encoding)
    return out_path_p


def write_json_with_text_file_ref(
    txt_path: str | Path,
    json_out_path: str | Path,
    *,
    key: str = "text_file",
    extra_fields: Optional[dict] = None,
    encoding: str = "utf-8",
    include_preview: bool = False,
    preview_chars: int = 500,
    include_hash: bool = True,
) -> Path:
    """
    Writes a small JSON that references the txt file path (NOT embedding the whole text).
    """
    txt = Path(txt_path)
    out = Path(json_out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # IMPORTANT: store repo-friendly path, not file:/// URI
    text_path = txt.as_posix().replace("\\", "/")

    repo = "klindqui/2d-material-database"
    branch = "main"

    payload = {
        "text_path": text_path,
        "text_url": f"https://github.com/{repo}/blob/{branch}/{text_path}",
        "text_raw_url": f"https://raw.githubusercontent.com/{repo}/{branch}/{text_path}",
    }


    meta = {"bytes": txt.stat().st_size}
    if include_hash:
        h = hashlib.sha256()
        with txt.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        meta["sha256"] = h.hexdigest()

    payload[f"{key}_meta"] = meta

    if include_preview:
        payload["text_preview"] = txt.read_text(encoding=encoding)[:preview_chars]

    if extra_fields:
        payload.update(extra_fields)

    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding=encoding)
    return out

def github_blob_url(repo_path: str, *, branch: str = "main") -> str:
    # repo_path like "Cleaned_TXT/10.1038_....txt"
    repo_path = repo_path.replace("\\", "/")
    return f"https://github.com/klindqui/2d-material-database/blob/{branch}/{repo_path}"

def github_raw_url(repo_path: str, *, branch: str = "main") -> str:
    repo_path = repo_path.replace("\\", "/")
    return f"https://raw.githubusercontent.com/klindqui/2d-material-database/{branch}/{repo_path}"
