"""Agent 3 — Difficulty Validation.

Checks that generated questions match the selected grade level and tags each
Easy/Medium/Hard. Backed by the fine-tuned difficulty-classification objective.
"""
from __future__ import annotations

from agents.base import Agent

SYSTEM = (
    "You are a difficulty labeler for Indian Classes 6-10. "
    "Given a list of exam questions, return ONLY the questions themselves, each prefixed with "
    "its difficulty tag [Easy], [Medium], or [Hard]. "
    "Output NOTHING else — no summaries, no validation reports, no explanations, no headers. "
    "Silently drop any question that is wildly off-grade-level."
)

agent = Agent(name="difficulty", system_prompt=SYSTEM)


def validate(questions: str, *, grade: int) -> str:
    return agent.run(
        f"Class {grade}. Label each question with [Easy], [Medium], or [Hard] and return "
        f"the full question text. No summaries or reports.\n\n{questions}"
    )
