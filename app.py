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
# App layout
# ---------------------------------------------------------------------------

def build_app() -> gr.Blocks:
    with gr.Blocks(title="TutorDesk AI") as demo:
        # Branded header (styled via #td-header in CUSTOM_CSS)
        gr.HTML(
            '<div id="td-header">'
            "<h1>TutorDesk AI</h1>"
            "<p>AI copilot for Indian tuition teachers &nbsp;·&nbsp; "
            "Classes 6–10 &nbsp;·&nbsp; Math &amp; Science &nbsp;·&nbsp; CBSE/NCERT</p>"
            "</div>"
        )

        with gr.Tabs():

            # ── Feature 2: Weekly Teaching Pack ──────────────────────────
            with gr.Tab("Weekly Teaching Pack"):
                gr.Markdown(
                    "Enter the chapter content and get a full teaching pack — "
                    "worksheet, homework, quiz, answer key, and parent note — in one click."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class"
                        )
                        subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject"
                        )
                        language = gr.Dropdown(
                            _lang_choices(), value="English", label="Language"
                        )
                        question_count = gr.Slider(
                            5, 30, value=20, step=5, label="Number of Questions"
                        )
                        difficulty = gr.Radio(
                            ["Easy", "Medium", "Hard"], value="Medium", label="Difficulty"
                        )
                    with gr.Column(scale=2):
                        chapter_text = gr.Textbox(
                            label="Chapter Content",
                            placeholder="Paste chapter text here, or use the Worksheet-from-Textbook tab to upload a photo.",
                            lines=10,
                        )

                generate_btn = gr.Button("Generate Teaching Pack", variant="primary")

                with gr.Tabs():
                    with gr.Tab("Worksheet"):
                        worksheet_out = gr.Markdown(label="Worksheet")
                    with gr.Tab("Homework"):
                        homework_out = gr.Markdown(label="Homework")
                    with gr.Tab("Quiz"):
                        quiz_out = gr.Markdown(label="Quiz")
                    with gr.Tab("Answer Key"):
                        key_out = gr.Markdown(label="Answer Key")
                    with gr.Tab("Parent Note"):
                        note_out = gr.Markdown(label="Parent Note Template")

                pdf_out = gr.File(label="Download PDF (all sections)")

                generate_btn.click(
                    fn=run_weekly_pack,
                    inputs=[grade, subject, chapter_text, question_count, difficulty, language],
                    outputs=[worksheet_out, homework_out, quiz_out, key_out, note_out, pdf_out],
                )

            # ── Feature 1: Worksheet-from-Textbook ───────────────────────
            with gr.Tab("Worksheet from Textbook"):
                gr.Markdown(
                    "Photograph a textbook chapter or upload a PDF — "
                    "MiniCPM-V (OpenBMB) reads it and auto-generates your full teaching pack."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        tb_grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class"
                        )
                        tb_subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject"
                        )
                        tb_language = gr.Dropdown(
                            _lang_choices(), value="English", label="Language"
                        )
                        tb_question_count = gr.Slider(
                            5, 30, value=20, step=5, label="Number of Questions"
                        )
                        tb_difficulty = gr.Radio(
                            ["Easy", "Medium", "Hard"], value="Medium", label="Difficulty"
                        )
                    with gr.Column(scale=2):
                        tb_photo = gr.Image(
                            label="Textbook Photo (camera or upload)",
                            type="pil",
                        )
                        tb_pdf = gr.File(
                            label="Or upload a PDF",
                            file_types=[".pdf"],
                        )

                tb_btn = gr.Button("Extract & Generate Teaching Pack", variant="primary")

                with gr.Tabs():
                    with gr.Tab("Worksheet"):
                        tb_worksheet = gr.Markdown(label="Worksheet")
                    with gr.Tab("Homework"):
                        tb_homework = gr.Markdown(label="Homework")
                    with gr.Tab("Quiz"):
                        tb_quiz = gr.Markdown(label="Quiz")
                    with gr.Tab("Answer Key"):
                        tb_key = gr.Markdown(label="Answer Key")
                    with gr.Tab("Parent Note"):
                        tb_note = gr.Markdown(label="Parent Note Template")

                tb_pdf_out = gr.File(label="Download PDF (all sections)")

                tb_btn.click(
                    fn=run_from_textbook,
                    inputs=[
                        tb_photo, tb_pdf,
                        tb_grade, tb_subject, tb_question_count, tb_difficulty, tb_language,
                    ],
                    outputs=[tb_worksheet, tb_homework, tb_quiz, tb_key, tb_note, tb_pdf_out],
                )

            # ── Feature 5: Photo Auto-Grading (Phase 4) ──────────────────
            with gr.Tab("Photo Auto-Grading"):
                gr.Markdown(
                    "Photograph a student's filled answer sheet. "
                    "MiniCPM-V (OpenBMB) reads the answers; the fine-tuned Qwen3-4B grades them "
                    "Indian-style — step marks, partial credit, CBSE conventions."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        ag_grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class"
                        )
                        ag_subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject"
                        )
                        ag_student = gr.Textbox(
                            label="Student Name", placeholder="e.g. Priya Sharma"
                        )
                    with gr.Column(scale=2):
                        ag_photo = gr.Image(
                            label="Answer Sheet Photo (camera or upload)",
                            type="pil",
                        )

                ag_scheme = gr.Textbox(
                    label="Marking Scheme",
                    placeholder=_SCHEME_PLACEHOLDER,
                    lines=8,
                    info="Use Q<n> [<marks> marks]: format. One line per question minimum.",
                )

                ag_btn = gr.Button("Grade Answer Sheet", variant="primary")

                ag_summary = gr.Markdown(label="Grade Summary")
                ag_note = gr.Textbox(label="Parent Note", lines=4, interactive=False)
                ag_pdf = gr.File(label="Download Grade Report (PDF)")

                ag_btn.click(
                    fn=run_auto_grade,
                    inputs=[ag_photo, ag_scheme, ag_student, ag_grade, ag_subject],
                    outputs=[ag_summary, ag_note, ag_pdf],
                )

            # ── Feature 3: Regional Language (Phase 5) ───────────────────
            with gr.Tab("Regional Language"):
                gr.Markdown(
                    "Translate any teaching content into your regional language using "
                    "**Tiny Aya** (CohereLabs/tiny-aya-fire, 3.35B, South-Asian-tuned). "
                    "Paste output from any other tab, choose a language, and download."
                )
                rl_language = gr.Dropdown(
                    _LANG_CHOICES_NON_EN,
                    value=_LANG_CHOICES_NON_EN[0] if _LANG_CHOICES_NON_EN else "Hindi",
                    label="Target Language",
                )
                rl_content = gr.Textbox(
                    label="Content to Translate",
                    placeholder="Paste worksheet, quiz, parent note, or any teaching content here…",
                    lines=12,
                )
                rl_btn = gr.Button("Translate with Tiny Aya", variant="primary")
                rl_out = gr.Textbox(label="Translated Output", lines=12, interactive=False)
                rl_pdf = gr.File(label="Download Translated PDF")

                rl_btn.click(
                    fn=run_localize,
                    inputs=[rl_content, rl_language],
                    outputs=[rl_out, rl_pdf],
                )

            # ── Feature 4: Illustrated Worksheets (Phase 5) ──────────────
            with gr.Tab("Illustrated Worksheets"):
                gr.Markdown(
                    "Generate a full teaching pack **with labeled diagrams** embedded in the PDF. "
                    "Qwen3-4B identifies concepts that benefit from a diagram; "
                    "**FLUX.1-schnell** (Black Forest Labs) generates them."
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        il_grade = gr.Dropdown(
                            _class_choices(), value="8", label="Class"
                        )
                        il_subject = gr.Dropdown(
                            _subject_choices(), value="Science", label="Subject"
                        )
                        il_language = gr.Dropdown(
                            _lang_choices(), value="English", label="Language"
                        )
                        il_question_count = gr.Slider(
                            5, 30, value=20, step=5, label="Number of Questions"
                        )
                        il_difficulty = gr.Radio(
                            ["Easy", "Medium", "Hard"], value="Medium", label="Difficulty"
                        )
                    with gr.Column(scale=2):
                        il_chapter_text = gr.Textbox(
                            label="Chapter Content",
                            placeholder="Paste chapter text here…",
                            lines=10,
                        )

                il_btn = gr.Button("Generate Illustrated Pack", variant="primary")
                il_diagram_status = gr.Textbox(
                    label="Diagram Status", interactive=False, lines=1
                )

                with gr.Tabs():
                    with gr.Tab("Worksheet"):
                        il_worksheet = gr.Markdown(label="Worksheet")
                    with gr.Tab("Homework"):
                        il_homework = gr.Markdown(label="Homework")
                    with gr.Tab("Quiz"):
                        il_quiz = gr.Markdown(label="Quiz")
                    with gr.Tab("Answer Key"):
                        il_key = gr.Markdown(label="Answer Key")
                    with gr.Tab("Parent Note"):
                        il_note = gr.Markdown(label="Parent Note")

                il_pdf = gr.File(label="Download Illustrated PDF (diagrams embedded)")

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

        # Footer
        gr.HTML(
            '<div id="td-footer">'
            "Built with ❤️ for Indian teachers · "
            "<a href='https://huggingface.co/naazimsnh02/tutordesk-qwen3-4b' "
            "target='_blank'>Fine-tuned Qwen3-4B</a> · "
            "Powered by Modal, MiniCPM-V, Tiny Aya &amp; FLUX.1-schnell"
            "</div>"
        )

    return demo


if __name__ == "__main__":
    # Gradio 6: theme= and css= go in launch(), not gr.Blocks()
    build_app().launch(theme=theme, css=CUSTOM_CSS)
