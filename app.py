"""TutorDesk AI — Gradio entry point (Hugging Face Space).

The Space is a thin client: all heavy inference runs on Modal (serving/modal_app.py).
Tabs are added phase by phase; stubs show "Coming soon" until their phase lands.
"""
from __future__ import annotations

import gradio as gr

from config import CONFIG
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
# App layout
# ---------------------------------------------------------------------------

def build_app() -> gr.Blocks:
    with gr.Blocks(title="TutorDesk AI") as demo:
        gr.Markdown(
            "# TutorDesk AI\n"
            "### AI copilot for Indian tuition teachers · Classes 6–10 · Math & Science · CBSE"
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
                        worksheet_out = gr.Textbox(label="Worksheet", lines=15)
                    with gr.Tab("Homework"):
                        homework_out = gr.Textbox(label="Homework", lines=10)
                    with gr.Tab("Quiz"):
                        quiz_out = gr.Textbox(label="Quiz", lines=10)
                    with gr.Tab("Answer Key"):
                        key_out = gr.Textbox(label="Answer Key", lines=15)
                    with gr.Tab("Parent Note"):
                        note_out = gr.Textbox(label="Parent Note Template", lines=6)

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
                        tb_worksheet = gr.Textbox(label="Worksheet", lines=15)
                    with gr.Tab("Homework"):
                        tb_homework = gr.Textbox(label="Homework", lines=10)
                    with gr.Tab("Quiz"):
                        tb_quiz = gr.Textbox(label="Quiz", lines=10)
                    with gr.Tab("Answer Key"):
                        tb_key = gr.Textbox(label="Answer Key", lines=15)
                    with gr.Tab("Parent Note"):
                        tb_note = gr.Textbox(label="Parent Note Template", lines=6)

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
                    "**Coming in Phase 4** — Photograph a student's filled answer sheet. "
                    "MiniCPM-V reads the answers; the fine-tuned Qwen3-4B grades them "
                    "Indian-style (step marks, partial credit)."
                )

            # ── Feature 3: Regional Language (Phase 5) ───────────────────
            with gr.Tab("Regional Language"):
                gr.Markdown(
                    "**Coming in Phase 5** — Regenerate any output in Hindi, Tamil, Telugu, "
                    "Bengali, Gujarati, or Marathi using Tiny Aya (CohereLabs)."
                )

            # ── Feature 4: Illustrated Worksheets (Phase 5) ──────────────
            with gr.Tab("Illustrated Worksheets"):
                gr.Markdown(
                    "**Coming in Phase 5** — Auto-generate labeled diagrams and figures "
                    "embedded in your worksheet PDF using FLUX (Black Forest Labs)."
                )

    return demo


if __name__ == "__main__":
    build_app().launch()
