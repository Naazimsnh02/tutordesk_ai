"""Print-ready PDF export — proper markdown rendering, polished A4 layout."""
from __future__ import annotations

import os
import re
import tempfile
import xml.etree.ElementTree as _ET

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

# ── Colour palette ────────────────────────────────────────────────────────────
_PRIMARY = colors.HexColor("#1a4a7a")   # dark navy
_ACCENT  = colors.HexColor("#2e7bcf")   # bright blue
_MUTED   = colors.HexColor("#6b7280")   # grey
_BLACK   = colors.HexColor("#1f2937")   # near-black
_RULE    = colors.HexColor("#d1dce8")   # light blue-grey rule

# ── Paragraph styles ──────────────────────────────────────────────────────────
_title_style = ParagraphStyle(
    "TDTitle",
    fontName="Helvetica-Bold",
    fontSize=20,
    textColor=_PRIMARY,
    spaceAfter=2,
    leading=24,
    alignment=TA_LEFT,
)
_subtitle_style = ParagraphStyle(
    "TDSubtitle",
    fontName="Helvetica",
    fontSize=11,
    textColor=_MUTED,
    spaceAfter=4,
    leading=14,
)
_h1_style = ParagraphStyle(
    "TDH1",
    fontName="Helvetica-Bold",
    fontSize=15,
    textColor=_PRIMARY,
    spaceBefore=14,
    spaceAfter=5,
    leading=19,
)
_h2_style = ParagraphStyle(
    "TDH2",
    fontName="Helvetica-Bold",
    fontSize=12,
    textColor=_ACCENT,
    spaceBefore=10,
    spaceAfter=3,
    leading=15,
)
_h3_style = ParagraphStyle(
    "TDH3",
    fontName="Helvetica-BoldOblique",
    fontSize=10,
    textColor=_BLACK,
    spaceBefore=7,
    spaceAfter=2,
    leading=13,
)
_body_style = ParagraphStyle(
    "TDBody",
    fontName="Helvetica",
    fontSize=10,
    textColor=_BLACK,
    leading=15,
    spaceAfter=4,
)
_bullet_style = ParagraphStyle(
    "TDBullet",
    fontName="Helvetica",
    fontSize=10,
    textColor=_BLACK,
    leading=15,
    spaceAfter=2,
)
_num_style = ParagraphStyle(
    "TDNum",
    fontName="Helvetica",
    fontSize=10,
    textColor=_BLACK,
    leading=15,
    spaceAfter=2,
)


# ── Inline markdown → ReportLab XML ──────────────────────────────────────────

def _md_inline(text: str) -> str:
    """Convert inline markdown to ReportLab-compatible XML tags."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold-italic (must come before bold/italic)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(?<![_])_(.+?)_(?![_])', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<font name="Courier" color="#c0392b">\1</font>', text)
    return text


# ── XML tag-nesting fixer ─────────────────────────────────────────────────────

_INLINE_TAGS = {"b", "i", "u", "strike", "super", "sub"}


def _fix_inline_tags(text: str) -> str:
    """Re-order mismatched inline closing tags so ReportLab can parse them.

    Model output frequently produces <b><i></b></i> instead of <b><i></i></b>.
    We walk the string with an open-tag stack and reorder closing tags to match.
    If the result is still invalid XML, we strip all inline tags as a last resort.
    """
    # Fast path: already valid
    try:
        _ET.fromstring(f"<para>{text}</para>")
        return text
    except _ET.ParseError:
        pass

    result: list[str] = []
    stack: list[str] = []
    pos = 0

    for m in re.finditer(r"<(/?)(\w+)([^>]*)>", text):
        result.append(text[pos : m.start()])
        pos = m.end()
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)

        if tag not in _INLINE_TAGS and not tag.startswith("font"):
            result.append(m.group(0))
            continue

        if not closing:
            stack.append(tag)
            result.append(f"<{tag}{attrs}>")
        else:
            if stack and stack[-1] == tag:
                stack.pop()
                result.append(f"</{tag}>")
            elif tag in stack:
                # Close inner tags first, then the target tag
                while stack and stack[-1] != tag:
                    result.append(f"</{stack.pop()}>")
                if stack:
                    stack.pop()
                result.append(f"</{tag}>")
            # else: orphan close tag — skip it

    result.append(text[pos:])
    while stack:
        result.append(f"</{stack.pop()}>")

    fixed = "".join(result)

    try:
        _ET.fromstring(f"<para>{fixed}</para>")
        return fixed
    except _ET.ParseError:
        # Last resort: strip all inline markup, keep plain text
        return re.sub(r"<[^>]+>", "", text)


def _safe_para(text: str, style) -> Paragraph:
    """Create a ReportLab Paragraph, healing tag-nesting errors from model output."""
    try:
        return Paragraph(text, style)
    except Exception:
        healed = _fix_inline_tags(text)
        try:
            return Paragraph(healed, style)
        except Exception:
            return Paragraph(re.sub(r"<[^>]+>", "", text), style)


# ── Block markdown parser ─────────────────────────────────────────────────────

def _parse_body(text: str) -> list:
    """Convert markdown text into a list of ReportLab flowables."""
    flowables: list = []
    lines = text.splitlines()
    bullet_buf: list[str] = []
    num_buf: list[str] = []

    def flush_bullets() -> None:
        if not bullet_buf:
            return
        items = [
            ListItem(
                _safe_para(_md_inline(b), _bullet_style),
                bulletColor=_ACCENT,
                leftIndent=8,
            )
            for b in bullet_buf
        ]
        flowables.append(
            ListFlowable(items, bulletType="bullet", start="•",
                         leftIndent=12, bulletFontSize=9, spaceAfter=4)
        )
        bullet_buf.clear()

    def flush_nums() -> None:
        if not num_buf:
            return
        items = [ListItem(_safe_para(_md_inline(t), _num_style)) for t in num_buf]
        flowables.append(
            ListFlowable(items, bulletType="1", leftIndent=16, spaceAfter=4)
        )
        num_buf.clear()

    i = 0
    while i < len(lines):
        raw  = lines[i]
        line = raw.strip()
        i += 1

        # Blank line
        if not line:
            flush_bullets()
            flush_nums()
            flowables.append(Spacer(1, 0.18 * cm))
            continue

        # Horizontal rule (--- or *** or ___)
        if re.fullmatch(r'[-*_]{3,}', line):
            flush_bullets()
            flush_nums()
            flowables.append(Spacer(1, 0.1 * cm))
            flowables.append(HRFlowable(width="100%", thickness=0.75, color=_RULE))
            flowables.append(Spacer(1, 0.1 * cm))
            continue

        # ATX headings
        if line.startswith('### '):
            flush_bullets(); flush_nums()
            flowables.append(_safe_para(_md_inline(line[4:]), _h3_style))
            continue
        if line.startswith('## '):
            flush_bullets(); flush_nums()
            flowables.append(_safe_para(_md_inline(line[3:]), _h2_style))
            continue
        if line.startswith('# '):
            flush_bullets(); flush_nums()
            flowables.append(_safe_para(_md_inline(line[2:]), _h1_style))
            continue

        # Unordered list item (-, *, +)
        m = re.match(r'^[-*+]\s+(.*)', line)
        if m:
            flush_nums()
            bullet_buf.append(m.group(1))
            continue

        # Ordered list item (1. or 1))
        m = re.match(r'^\d+[.)]\s+(.*)', line)
        if m:
            flush_bullets()
            num_buf.append(m.group(1))
            continue

        # Regular body text
        flush_bullets()
        flush_nums()
        flowables.append(_safe_para(_md_inline(line), _body_style))

    flush_bullets()
    flush_nums()
    return flowables


# ── Page decorator (header rule + footer) ─────────────────────────────────────

def _make_page_decorator(doc_title: str):
    def _decorate(canvas, doc):
        canvas.saveState()
        w, h = A4

        # Top accent rule
        canvas.setStrokeColor(_PRIMARY)
        canvas.setLineWidth(2)
        canvas.line(2 * cm, h - 1.3 * cm, w - 2 * cm, h - 1.3 * cm)

        # Footer
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(_MUTED)
        canvas.drawString(2 * cm, 0.8 * cm, "TutorDesk AI")
        canvas.drawCentredString(w / 2, 0.8 * cm, doc_title)
        canvas.drawRightString(w - 2 * cm, 0.8 * cm, f"Page {doc.page}")

        canvas.restoreState()
    return _decorate


# ── Public API ────────────────────────────────────────────────────────────────

def to_pdf(
    title: str,
    subtitle: str,
    body: str,
    *,
    images: list | None = None,
    out_path: str | None = None,
) -> str:
    """Render title + subtitle + markdown body to a print-ready A4 PDF.

    Returns the file path. If out_path is None a temp file is created.
    Optionally embeds PIL images (FLUX diagrams) after the body text.
    """
    if out_path is None:
        fd, out_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

    decorate = _make_page_decorator(title)

    doc = SimpleDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        onFirstPage=decorate,
        onLaterPages=decorate,
    )

    story: list = [
        _safe_para(title, _title_style),
        _safe_para(subtitle, _subtitle_style),
        Spacer(1, 0.15 * cm),
        HRFlowable(width="100%", thickness=1.5, color=_ACCENT),
        Spacer(1, 0.35 * cm),
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
