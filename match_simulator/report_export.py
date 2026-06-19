"""리포트 HTML/PDF 내보내기."""

from __future__ import annotations

import html
import re
from datetime import datetime


def markdown_to_html(report: str, title: str = "매치 리포트") -> str:
    safe = html.escape(report)
    body = safe
    body = re.sub(r"^### (.+)$", r"<h3>\1</h3>", body, flags=re.MULTILINE)
    body = re.sub(r"^## (.+)$", r"<h2>\1</h2>", body, flags=re.MULTILINE)
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"\n\n", "<br/><br/>", body)
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<style>
body {{ font-family: "Malgun Gothic", sans-serif; max-width: 800px; margin: 2rem auto; line-height: 1.6; }}
h2 {{ color: #E02020; border-bottom: 2px solid #1a1a1a; padding-bottom: 0.3rem; }}
h3 {{ color: #059669; }}
@media print {{ body {{ margin: 1cm; }} }}
</style></head><body>
<p style="color:#666;font-size:0.85rem">생성: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
{body}
</body></html>"""


def report_to_pdf_bytes(report: str, title: str = "Match Report") -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/malgunbd.ttf",
    ]
    font_loaded = False
    for path in font_paths:
        try:
            pdf.add_font("Korean", "", path)
            pdf.set_font("Korean", size=10)
            font_loaded = True
            break
        except Exception:
            continue

    if not font_loaded:
        pdf.set_font("Helvetica", size=10)

    pdf.set_title(title)
    pdf.cell(0, 8, title, ln=True)
    pdf.ln(4)

    for line in report.splitlines():
        text = line.strip()
        if not text:
            pdf.ln(3)
            continue
        text = re.sub(r"[#*`>]", "", text)
        try:
            pdf.multi_cell(0, 6, text)
        except Exception:
            pdf.multi_cell(0, 6, text.encode("latin-1", errors="replace").decode("latin-1"))

    out = pdf.output()
    return out if isinstance(out, bytes) else out.encode("latin-1")
