"""TutorDesk AI — Gradio 6 entry point (Hugging Face Space).

The Space is a thin client: all heavy inference runs on Modal (serving/modal_app.py).
Custom theme + CSS lives in frontend/theme.py (Off-Brand badge).
In Gradio 6, theme= and css= are passed to demo.launch(), not gr.Blocks().
"""
from __future__ import annotations

import gradio as gr

from config import CONFIG
from frontend.theme import CUSTOM_CSS, theme
from models.aya import localize
from pipelines.auto_grade import grade_sheet
from pipelines.illustrated_worksheet import build_illustrated_pack
from pipelines.weekly_pack import build_pack
from pipelines.worksheet_from_textbook import from_image, from_pdf


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _class_choices() -> list[str]:
    return [str(c) for c in CONFIG.classes]


def _subject_choices() -> list[str]:
    return list(CONFIG.subjects)


def _lang_choices() -> list[str]:
    return list(CONFIG.languages)


# ---------------------------------------------------------------------------
# Feature 2 — Weekly Teaching Pack
# ---------------------------------------------------------------------------

def run_weekly_pack(
    grade: str,
    subject: str,
    chapter_text: str,
    question_count: int,
    difficulty: str,
    language: str,
) -> tuple[str, str, str, str, str, str]:
    """Called by the Gradio button. Returns (worksheet, homework, quiz, key, note, pdf_path)."""
    if not chapter_text.strip():
        msg = "Please enter chapter text or use Feature 1 (Worksheet-from-Textbook) to upload a photo."
        return msg, "", "", "", "", None

    pack = build_pack(
        chapter_text,
        grade=int(grade),
        subject=subject,
        question_count=int(question_count),
        diff=difficulty,
        language=language,
    )
    pdf_path = pack.to_pdf(grade=int(grade), subject=subject, chapter=chapter_text[:60])
    return (
        pack.worksheet,
        pack.homework,
        pack.quiz,
        pack.answer_key,
        pack.parent_note,
        pdf_path,
    )


# ---------------------------------------------------------------------------
# Feature 1 — Worksheet-from-Textbook
# ---------------------------------------------------------------------------

def run_from_textbook(
    photo,
    pdf_file,
    grade: str,
    subject: str,
    question_count: int,
    difficulty: str,
    language: str,
) -> tuple[str, str, str, str, str, str]:
    """Called by the Gradio button. Accepts either a photo (PIL) or a PDF file path."""
    if photo is None and pdf_file is None:
        msg = "Please upload a textbook photo or PDF."
        return msg, "", "", "", "", None

    try:
        if photo is not None:
            from PIL import Image as PILImage
            img = PILImage.fromarray(photo) if not hasattr(photo, "save") else photo
            pack = from_image(
                img,
                grade=int(grade),
                subject=subject,
                question_count=int(question_count),
                diff=difficulty,
                language=language,
            )
        else:
            pack = from_pdf(
                pdf_file,
                grade=int(grade),
                subject=subject,
                question_count=int(question_count),
                diff=difficulty,
                language=language,
            )
    except NotImplementedError as exc:
        return str(exc), "", "", "", "", None

    pdf_path = pack.to_pdf(grade=int(grade), subject=subject, chapter="Textbook upload")
    return (
        pack.worksheet,
        pack.homework,
        pack.quiz,
        pack.answer_key,
        pack.parent_note,
        pdf_path,
    )


# ---------------------------------------------------------------------------
# Feature 5 — Photo Auto-Grading
# ---------------------------------------------------------------------------

_SCHEME_PLACEHOLDER = (
    "Q1 [3 marks]: Model answer for question 1\n"
    "Q2 [5 marks]:\n"
    "  Step 1 (1 mark): First step expected\n"
    "  Step 2 (2 marks): Second step expected\n"
    "  Step 3 (2 marks): Final answer expected\n"
    "Q3 [2 marks]: Model answer for question 3"
)


def run_auto_grade(
    photo,
    marking_scheme: str,
    student_name: str,
    grade: str,
    subject: str,
) -> tuple[str, str, str | None]:
    """Called by the Gradio button. Returns (grade_summary_md, parent_note, pdf_path)."""
    if photo is None:
        return "Please upload a photo of the student's answer sheet.", "", None
    if not marking_scheme.strip():
        return "Please enter the marking scheme using the Q[N marks] template.", "", None

    from PIL import Image as PILImage

    img = PILImage.fromarray(photo) if not hasattr(photo, "save") else photo
    student = student_name.strip() or "Student"

    try:
        result = grade_sheet(
            img,
            marking_scheme=marking_scheme,
            grade=int(grade),
            subject=subject,
            student=student,
        )
    except NotImplementedError as exc:
        return str(exc), "", None

    pdf_path = result.to_pdf()
    return result.summary_markdown(), result.parent_note, pdf_path


# ---------------------------------------------------------------------------
# Feature 3 — Regional Language (Tiny Aya)
# ---------------------------------------------------------------------------

_LANG_CHOICES_NON_EN = [l for l in CONFIG.languages if l.lower() != "english"]


def run_localize(content: str, language: str) -> tuple[str, str | None]:
    """Translate `content` to `language` via Tiny Aya. Returns (localized_text, pdf_path)."""
    if not content.strip():
        return "Please paste some content to translate.", None
    if language.lower() == "english":
        return content, None
    try:
        localized = localize(content, language=language)
    except NotImplementedError as exc:
        return str(exc), None

    from utils.pdf import to_pdf as _to_pdf
    pdf_path = _to_pdf(
        title=f"TutorDesk AI — {language} Output",
        subtitle="Translated by Tiny Aya (CohereLabs/tiny-aya-fire)",
        body=localized,
    )
    return localized, pdf_path


# ---------------------------------------------------------------------------
# Feature 4 — Illustrated Worksheets (FLUX.1-schnell)
# ---------------------------------------------------------------------------

def run_illustrated_pack(
    grade: str,
    subject: str,
    chapter_text: str,
    question_count: int,
    difficulty: str,
    language: str,
) -> tuple[str, str, str, str, str, str, str]:
    """Returns (worksheet, homework, quiz, key, note, diagram_status, pdf_path)."""
    if not chapter_text.strip():
        msg = "Please enter chapter text."
        return msg, "", "", "", "", "", None

    result = build_illustrated_pack(
        chapter_text,
        grade=int(grade),
        subject=subject,
        question_count=int(question_count),
        diff=difficulty,
        language=language,
    )
    pack = result.pack
    n = result.diagram_count
    diagram_status = (
        f"{n} diagram(s) generated and embedded in PDF."
        if n > 0
        else "No diagrams generated (FLUX unavailable or offline — text-only PDF)."
    )
    return (
        pack.worksheet,
        pack.homework,
        pack.quiz,
        pack.answer_key,
        pack.parent_note,
        diagram_status,
        result.pdf_path,
    )


# ---------------------------------------------------------------------------
# HTML snippet helpers
# ---------------------------------------------------------------------------

def _banner(icon: str, title: str, desc: str) -> str:
    return (
        f'<div class="feature-banner">'
        f'<strong>{icon} {title}</strong> — {desc}'
        f'</div>'
    )


_DIVIDER = '<hr class="td-divider">'
_OUTPUT_LABEL = '<div class="td-output-label">Generated Output</div>'


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------

def build_app() -> gr.Blocks:
    with gr.Blocks(title="TutorDesk AI") as demo:

        # ── Header ──────────────────────────────────────────────────────────
        gr.HTML(
            '<div id="td-header">'
            '<span class="td-icon">📚</span>'
            '<h1>TutorDesk AI</h1>'
            '<p class="td-tagline">'
            'AI copilot for Indian tuition teachers &nbsp;·&nbsp; '
            '90 min/day of prep → under 10'
            '</p>'
            '<div class="td-badges">'
            '<span class="td-badge">📖 Classes 6–10</span>'
            '<span class="td-badge">🔬 Math &amp; Science</span>'
            '<span class="td-badge">📋 CBSE / NCERT</span>'
            '<span class="td-badge">🇮🇳 7 Languages</span>'
            '<span class="td-badge">⚡ Modal GPU</span>'
            '<span class="td-badge">≤ 32B Params</span>'
            '</div>'
            '</div>'
        )

        with gr.Tabs():

            # ── Feature 2: Weekly Teaching Pack ──────────────────────────
            with gr.Tab("📅 Weekly Pack"):
                gr.HTML(_banner(
                    "📅", "Weekly Teaching Pack",
                    "Enter chapter content and get a full teaching pack — "
                    "worksheet, homework, quiz, answer key, and parent note — in one click."
                ))
                with gr.Row(elem_classes=["td-main-row"]):
                    with gr.Column(scale=1, elem_classes=["settings-panel"]):
                        grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class", elem_id="wp-grade"
                        )
                        subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject", elem_id="wp-subject"
                        )
                        language = gr.Dropdown(
                            _lang_choices(), value="English", label="Language", elem_id="wp-lang"
                        )
                        question_count = gr.Slider(
                            5, 30, value=20, step=5, label="Questions", elem_id="wp-count"
                        )
                        difficulty = gr.Radio(
                            ["Easy", "Medium", "Hard"], value="Medium", label="Difficulty",
                            elem_id="wp-diff", elem_classes=["radio-group"],
                        )
                    with gr.Column(scale=2, elem_classes=["content-panel"]):
                        chapter_text = gr.Textbox(
                            label="Chapter Content",
                            placeholder="Paste chapter text here, or use the Textbook Scan tab to upload a photo.",
                            lines=10,
                            elem_id="wp-chapter",
                        )

                gr.HTML(_DIVIDER)
                generate_btn = gr.Button("✨ Generate Teaching Pack", variant="primary", elem_id="wp-btn")
                gr.HTML(_OUTPUT_LABEL)

                with gr.Tabs():
                    with gr.Tab("📝 Worksheet"):
                        worksheet_out = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("📚 Homework"):
                        homework_out = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("❓ Quiz"):
                        quiz_out = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("🔑 Answer Key"):
                        key_out = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("👨‍👩‍👧 Parent Note"):
                        note_out = gr.Markdown(elem_classes=["output-markdown"])

                pdf_out = gr.File(
                    label="⬇️ Download PDF — all sections",
                    elem_classes=["td-pdf-download"],
                )

                generate_btn.click(
                    fn=run_weekly_pack,
                    inputs=[grade, subject, chapter_text, question_count, difficulty, language],
                    outputs=[worksheet_out, homework_out, quiz_out, key_out, note_out, pdf_out],
                )

            # ── Feature 1: Worksheet-from-Textbook ───────────────────────
            with gr.Tab("📷 Textbook Scan"):
                gr.HTML(_banner(
                    "📷", "Worksheet from Textbook",
                    "Photograph a textbook chapter or upload a PDF — "
                    "<strong>MiniCPM-V</strong> (OpenBMB) reads it and auto-generates your full teaching pack."
                ))
                with gr.Row(elem_classes=["td-main-row"]):
                    with gr.Column(scale=1, elem_classes=["settings-panel"]):
                        tb_grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class", elem_id="tb-grade"
                        )
                        tb_subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject", elem_id="tb-subject"
                        )
                        tb_language = gr.Dropdown(
                            _lang_choices(), value="English", label="Language", elem_id="tb-lang"
                        )
                        tb_question_count = gr.Slider(
                            5, 30, value=20, step=5, label="Questions", elem_id="tb-count"
                        )
                        tb_difficulty = gr.Radio(
                            ["Easy", "Medium", "Hard"], value="Medium", label="Difficulty",
                            elem_id="tb-diff", elem_classes=["radio-group"],
                        )
                    with gr.Column(scale=2, elem_classes=["content-panel"]):
                        tb_photo = gr.Image(
                            label="Textbook Photo (camera or upload)",
                            type="pil",
                            elem_id="tb-photo",
                        )
                        tb_pdf = gr.File(
                            label="Or upload a PDF",
                            file_types=[".pdf"],
                            elem_id="tb-pdf-in",
                        )

                gr.HTML(_DIVIDER)
                tb_btn = gr.Button(
                    "🔍 Extract & Generate Teaching Pack", variant="primary", elem_id="tb-btn"
                )
                gr.HTML(_OUTPUT_LABEL)

                with gr.Tabs():
                    with gr.Tab("📝 Worksheet"):
                        tb_worksheet = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("📚 Homework"):
                        tb_homework = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("❓ Quiz"):
                        tb_quiz = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("🔑 Answer Key"):
                        tb_key = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("👨‍👩‍👧 Parent Note"):
                        tb_note = gr.Markdown(elem_classes=["output-markdown"])

                tb_pdf_out = gr.File(
                    label="⬇️ Download PDF — all sections",
                    elem_classes=["td-pdf-download"],
                )

                tb_btn.click(
                    fn=run_from_textbook,
                    inputs=[
                        tb_photo, tb_pdf,
                        tb_grade, tb_subject, tb_question_count, tb_difficulty, tb_language,
                    ],
                    outputs=[tb_worksheet, tb_homework, tb_quiz, tb_key, tb_note, tb_pdf_out],
                )

            # ── Feature 5: Photo Auto-Grading ────────────────────────────
            with gr.Tab("✏️ Auto-Grade"):
                gr.HTML(_banner(
                    "✏️", "Photo Auto-Grading",
                    "Photograph a student's filled answer sheet. "
                    "<strong>MiniCPM-V</strong> reads the answers; the fine-tuned "
                    "<strong>Qwen3-4B</strong> grades them Indian-style — "
                    "step marks, partial credit, CBSE conventions."
                ))
                with gr.Row(elem_classes=["td-main-row"]):
                    with gr.Column(scale=1, elem_classes=["settings-panel"]):
                        ag_grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class", elem_id="ag-grade"
                        )
                        ag_subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject", elem_id="ag-subject"
                        )
                        ag_student = gr.Textbox(
                            label="Student Name",
                            placeholder="e.g. Priya Sharma",
                            elem_id="ag-student",
                        )
                    with gr.Column(scale=2, elem_classes=["content-panel"]):
                        ag_photo = gr.Image(
                            label="Answer Sheet Photo (camera or upload)",
                            type="pil",
                            elem_id="ag-photo",
                        )

                ag_scheme = gr.Textbox(
                    label="Marking Scheme",
                    placeholder=_SCHEME_PLACEHOLDER,
                    lines=8,
                    info="Use Q<n> [<marks> marks]: format. One line per question minimum.",
                    elem_id="ag-scheme",
                )

                gr.HTML(_DIVIDER)
                ag_btn = gr.Button("🎯 Grade Answer Sheet", variant="primary", elem_id="ag-btn")
                gr.HTML('<div class="td-output-label">Grading Results</div>')

                ag_summary = gr.Markdown(
                    elem_id="ag-summary",
                    elem_classes=["output-markdown"],
                )
                ag_note = gr.Textbox(
                    label="Parent Note",
                    lines=4,
                    interactive=False,
                    elem_id="ag-note",
                )
                ag_pdf = gr.File(
                    label="⬇️ Download Grade Report (PDF)",
                    elem_classes=["td-pdf-download"],
                )

                ag_btn.click(
                    fn=run_auto_grade,
                    inputs=[ag_photo, ag_scheme, ag_student, ag_grade, ag_subject],
                    outputs=[ag_summary, ag_note, ag_pdf],
                )

            # ── Feature 3: Regional Language ─────────────────────────────
            with gr.Tab("🌐 Translate"):
                gr.HTML(_banner(
                    "🌐", "Regional Language",
                    "Translate any teaching content into your regional language using "
                    "<strong>Tiny Aya</strong> (CohereLabs/tiny-aya-fire, 3.35 B, South-Asian-tuned). "
                    "Paste output from any other tab, choose a language, and download."
                ))
                rl_language = gr.Dropdown(
                    _LANG_CHOICES_NON_EN,
                    value=_LANG_CHOICES_NON_EN[0] if _LANG_CHOICES_NON_EN else "Hindi",
                    label="Target Language",
                    elem_id="rl-lang",
                )
                rl_content = gr.Textbox(
                    label="Content to Translate",
                    placeholder="Paste worksheet, quiz, parent note, or any teaching content here…",
                    lines=12,
                    elem_id="rl-content",
                )
                gr.HTML(_DIVIDER)
                rl_btn = gr.Button("🌐 Translate with Tiny Aya", variant="primary", elem_id="rl-btn")
                gr.HTML('<div class="td-output-label">Translated Output</div>')
                rl_out = gr.Textbox(
                    label="Translated Output",
                    lines=12,
                    interactive=False,
                    elem_id="rl-out",
                )
                rl_pdf = gr.File(
                    label="⬇️ Download Translated PDF",
                    elem_classes=["td-pdf-download"],
                )

                rl_btn.click(
                    fn=run_localize,
                    inputs=[rl_content, rl_language],
                    outputs=[rl_out, rl_pdf],
                )

            # ── Feature 4: Illustrated Worksheets ────────────────────────
            with gr.Tab("🎨 Illustrated"):
                gr.HTML(_banner(
                    "🎨", "Illustrated Worksheets",
                    "Generate a full teaching pack <strong>with labeled diagrams</strong> embedded in the PDF. "
                    "Qwen3-4B identifies key concepts; "
                    "<strong>FLUX.1-schnell</strong> (Black Forest Labs) generates the images."
                ))
                with gr.Row(elem_classes=["td-main-row"]):
                    with gr.Column(scale=1, elem_classes=["settings-panel"]):
                        il_grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class", elem_id="il-grade"
                        )
                        il_subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject", elem_id="il-subject"
                        )
                        il_language = gr.Dropdown(
                            _lang_choices(), value="English", label="Language", elem_id="il-lang"
                        )
                        il_question_count = gr.Slider(
                            5, 30, value=20, step=5, label="Questions", elem_id="il-count"
                        )
                        il_difficulty = gr.Radio(
                            ["Easy", "Medium", "Hard"], value="Medium", label="Difficulty",
                            elem_id="il-diff", elem_classes=["radio-group"],
                        )
                    with gr.Column(scale=2, elem_classes=["content-panel"]):
                        il_chapter_text = gr.Textbox(
                            label="Chapter Content",
                            placeholder="Paste chapter text here…",
                            lines=10,
                            elem_id="il-chapter",
                        )

                gr.HTML(_DIVIDER)
                il_btn = gr.Button(
                    "🎨 Generate Illustrated Pack", variant="primary", elem_id="il-btn"
                )
                il_diagram_status = gr.Textbox(
                    label="Diagram Status",
                    interactive=False,
                    lines=1,
                    elem_id="il-status",
                )
                gr.HTML(_OUTPUT_LABEL)

                with gr.Tabs():
                    with gr.Tab("📝 Worksheet"):
                        il_worksheet = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("📚 Homework"):
                        il_homework = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("❓ Quiz"):
                        il_quiz = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("🔑 Answer Key"):
                        il_key = gr.Markdown(elem_classes=["output-markdown"])
                    with gr.Tab("👨‍👩‍👧 Parent Note"):
                        il_note = gr.Markdown(elem_classes=["output-markdown"])

                il_pdf = gr.File(
                    label="⬇️ Download Illustrated PDF (diagrams embedded)",
                    elem_classes=["td-pdf-download"],
                )

                il_btn.click(
                    fn=run_illustrated_pack,
                    inputs=[
                        il_grade, il_subject, il_chapter_text,
                        il_question_count, il_difficulty, il_language,
                    ],
                    outputs=[
                        il_worksheet, il_homework, il_quiz,
                        il_key, il_note, il_diagram_status, il_pdf,
                    ],
                )

        # ── Footer ───────────────────────────────────────────────────────────
        gr.HTML(
            '<div id="td-footer">'
            '<div class="td-footer-badges">'
            '<span class="td-footer-badge">Qwen3-4B Fine-tuned</span>'
            '<span class="td-footer-badge">MiniCPM-V 8B</span>'
            '<span class="td-footer-badge">Tiny Aya 3.35B</span>'
            '<span class="td-footer-badge">FLUX.1-schnell</span>'
            '<span class="td-footer-badge">Modal GPU</span>'
            '<span class="td-footer-badge">HF × Gradio Hackathon 2026</span>'
            '</div>'
            '<div class="td-footer-text">'
            'Built with ❤️ for Indian teachers &nbsp;·&nbsp; '
            '<a href="https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b" target="_blank">'
            'Fine-tuned Qwen3-4B</a> &nbsp;·&nbsp; '
            'Powered by Modal, MiniCPM-V, Tiny Aya &amp; FLUX.1-schnell'
            '</div>'
            '</div>'
        )

    return demo


if __name__ == "__main__":
    # Gradio 6: theme= and css= go in launch(), not gr.Blocks()
    build_app().launch(theme=theme, css=CUSTOM_CSS)
