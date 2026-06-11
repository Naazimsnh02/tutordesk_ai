"""TutorDesk AI — Gradio entry point (Hugging Face Space).

Phase 0: minimal "hello" app so the Space goes live.
Later phases wire in the pipelines (weekly_pack, worksheet_from_textbook, auto_grade).
A custom gr.Server frontend (frontend/) replaces the default layout to claim Off-Brand.
"""
from __future__ import annotations

import gradio as gr

from config import CONFIG


def _status() -> str:
    return (
        f"TutorDesk AI ready · scope: Classes {CONFIG.classes}, {CONFIG.subjects}, "
        f"{CONFIG.board} · offline={CONFIG.offline} · vision={CONFIG.minicpm_model}"
    )


def build_app() -> gr.Blocks:
    with gr.Blocks(title="TutorDesk AI") as demo:
        gr.Markdown("# TutorDesk AI\n### AI copilot for Indian tuition teachers")
        gr.Markdown(_status())

        # TODO Phase 1: Weekly Teaching Pack tab
        # TODO Phase 2: Worksheet-from-Textbook tab
        # TODO Phase 4: Photo Auto-Grading tab
        # TODO Phase 5: language selector + diagram toggle

    return demo


if __name__ == "__main__":
    build_app().launch()
