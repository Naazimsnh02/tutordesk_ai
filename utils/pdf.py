"""Print-ready PDF export — every teacher output is a downloadable/printable A4 PDF."""
from __future__ import annotations

import os
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as RLImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

_styles = getSampleStyleSheet()

_title_style = ParagraphStyle(
    "TDTitle",
    parent=_styles["Title"],
    fontSize=16,
    spaceAfter=6,
)
_subtitle_style = ParagraphStyle(
    "TDSubtitle",
    parent=_styles["Normal"],
    fontSize=11,
    textColor="#555555",
    spaceAfter=12,
)
_body_style = ParagraphStyle(
    "TDBody",
    parent=_styles["Normal"],
    fontSize=10,
    leading=15,
    spaceAfter=4,
)
_section_style = ParagraphStyle(
    "TDSection",
    parent=_styles["Heading2"],
    fontSize=12,
    spaceBefore=12,
    spaceAfter=4,
)


def _parse_body(text: str) -> list:
    """Convert plain text (with blank-line sections) into reportlab flowables."""
    flowables = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 0.2 * cm))
        elif stripped.startswith("##"):
            flowables.append(Paragraph(stripped.lstrip("#").strip(), _section_style))
        else:
            safe = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            flowables.append(Paragraph(safe, _body_style))
    return flowables


def to_pdf(
    title: str,
    subtitle: str,
    body: str,
    *,
    images: list | None = None,
    out_path: str | None = None,
) -> str:
    """Render `title` + `subtitle` + `body` to a print-ready A4 PDF.

    Returns the file path. If `out_path` is None a temp file is created.
    Optionally embeds PIL images (FLUX diagrams) after the body text.
    """
    if out_path is None:
        fd, out_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = [
        Paragraph(title, _title_style),
        Paragraph(subtitle, _subtitle_style),
        Spacer(1, 0.4 * cm),
        *_parse_body(body),
    ]

    if images:
        story.append(Spacer(1, 0.5 * cm))
        for img in images:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            img.save(tmp.name)
            max_w = 15 * cm
            w, h = img.size
            ratio = min(max_w / w, 10 * cm / h)
            story.append(RLImage(tmp.name, width=w * ratio, height=h * ratio))
            story.append(Spacer(1, 0.3 * cm))

    doc.build(story)
    return out_path
